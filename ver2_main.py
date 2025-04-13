#Backend imports
import spo2_calculation
import neurokit_peak_detection
import numpy as np
import threading
import asyncio
import websockets
import traceback
import json
#Frontend imports
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Line, Color

# Constants
ESP32_WS_URL = "ws://192.168.4.1/ws"
T = 5  # Time in seconds for calculations
BUFFER_SIZE = T*400  # Number of elements to collect before processing
color_warning = (254 / 255, 61 / 255, 96 / 255)
color_good = (12 / 255, 234 / 255, 194 / 255, 1)

# Window settings
Window.size = (500, 700)
Builder.load_file('pulse_ox.kv')

class WebSocketClient:
    # WebSocket client for real-time data acquisition
    def __init__(self, uri, data_callback):
        self.uri = uri
        self.data_callback = data_callback  # Callback function to handle received data
        self.is_running = False  # Flag to control whether the WebSocket client is running
        self.start_websocket_client()

    # Start the WebSocket client in a separate thread
    def start_websocket_client(self):
        loop = asyncio.new_event_loop()
        threading.Thread(target=self.websocket_thread, args=(loop,), daemon=True).start()

    # Run the asyncio event loop in a separate thread
    def websocket_thread(self, loop):
        loop.run_until_complete(self.websocket_task(loop))

    # Connect to the WebSocket and continuously receive messages
    async def websocket_task(self, loop):
        while self.is_running:
            try:
                async with websockets.connect(self.uri, ping_interval=None) as websocket:
                    while self.is_running:
                        try:
                            message = await websocket.recv()
                            Clock.schedule_once(lambda dt: self.data_callback(message))  # Schedule UI update
                        except websockets.ConnectionClosedError as e:
                            print(f"Connection closed: {e}")
                            raise e
            except websockets.ConnectionClosedError as e:
                print(f"Reconnecting in 5 seconds due to: {e}")
                await asyncio.sleep(5)
            except Exception as e:
                print(f"Unexpected error: {e}. Retrying in 5 seconds...")
                traceback.print_exc()
                await asyncio.sleep(5)

    def stop(self):
        """Stop the WebSocket client."""
        self.is_running = False

class PulseOxLayout(Widget):
    def __init__(self, **kwargs):
        super(PulseOxLayout, self).__init__(**kwargs)
        self.line = Line(points=[], width=2)
        self.ids.box.canvas.add(self.line)
        
        # Initialize WebSocket Client (initially disabled)
        self.websocket_client = WebSocketClient(ESP32_WS_URL, self.process_websocket_data)
        
        self.is_recording = False  # Flag to control recording state
        self.data_buffer = {'red': [], 'ir': []}  # Data buffer to store elements until minimum of T*400 (time * # elements per sec) elements 
        self.timestamps_buffer = []  # Buffer for timestamps

    # Process incoming WebSocket data and update GUI
    def process_websocket_data(self, message):
        try:
            # Parse the incoming JSON message into a dictionary
            data = json.loads(message)

            # Extract the lists from the JSON message
            timestamps = data.get("timestamps", [])
            r_data = data.get("red", [])
            ir_data = data.get("ir", [])

            if len(r_data) != len(ir_data) or len(r_data) != len(timestamps):
                print(f"Error: Data length mismatch. Red: {len(r_data)}, IR: {len(ir_data)}, Timestamps: {len(timestamps)}")
                return

            # Add the incoming data to the buffer
            self.timestamps_buffer.extend(timestamps)
            self.data_buffer['red'].extend(r_data)
            self.data_buffer['ir'].extend(ir_data)

            # Check if we have accumulated T*400 data points
            if len(self.data_buffer['red']) >= BUFFER_SIZE:
                # Process the first T*400 elements
                r_segment = self.data_buffer['red'][:BUFFER_SIZE]
                ir_segment = self.data_buffer['ir'][:BUFFER_SIZE]
                timestamps_segment = self.timestamps_buffer[:BUFFER_SIZE]

                r_segment = np.array(r_segment, dtype=np.float64)
                ir_segment = np.array(ir_segment, dtype=np.float64)

                # Process the data
                self.process_data(r_segment, ir_segment, timestamps_segment)

                # Remove the processed data from the buffer
                self.data_buffer['red'] = self.data_buffer['red'][BUFFER_SIZE:]
                self.data_buffer['ir'] = self.data_buffer['ir'][BUFFER_SIZE:]
                self.timestamps_buffer = self.timestamps_buffer[BUFFER_SIZE:]

        except Exception as e:
            print(f"Error processing data: {e}")
            traceback.print_exc()
    
    # 3rd degree polynomial detrending
    def detrend_data(self, r_segment, ir_segment, time_stamps):
        light_data = [r_segment, ir_segment]
        x_values = np.array(time_stamps)
        for i in range(2):
            y_values = np.array(light_data[i])

            coeffs = np.polyfit(x_values, y_values, 3)
            
            # The last coefficient of polynomial fit was ommitted to prevent the removal of the DC component
            fitted_line = [coeffs[0]*j**3 + coeffs[1]*j**2 + coeffs[2]*j for j in x_values]


            light_data[i] = light_data[i] - fitted_line

        ret_r_data = light_data[0]
        ret_ir_data = light_data[1]
        return ret_r_data, ret_ir_data

    # Process the collected data segment and update the UI
    def process_data(self, r_segment, ir_segment, timestamps_segment):
        # Coverting timestamps into minutes
        timestamps_segment = [x/(1000*60) for x in timestamps_segment]
        # Detrending data prior to processing
        r_segment, ir_segment = self.detrend_data(r_segment, ir_segment, timestamps_segment)


        # Running peak detection on the IR segment
        peak_locs = neurokit_peak_detection.get_peak_locs(ir_segment)[1].get("PPG_Peaks", [])
        HR = (len(peak_locs) - 1) / (timestamps_segment[-1]-timestamps_segment[0]) # Convert to BPM
        _, _, _, _, _, spo2 = spo2_calculation.calc_spo2(r_segment, ir_segment, peak_locs)

        # Updating GUI info
        self.ids.HR_data.text = f'{HR:.1f} bpm'
        self.ids.spO2_data.text = f'{spo2:.1f} %'

        # Changing color based on HR and SpO2 values (danger levels)
        self.ids.HR_data.color = color_warning if (HR > 100 or HR < 60) else color_good
        self.ids.HR_title.color = self.ids.HR_data.color

        self.ids.spO2_data.color = color_warning if (spo2 < 92) else color_good
        self.ids.spO2_title.color = self.ids.spO2_data.color

        # Generating graph points (scaled to fit within the window)
        plotting_points = [
            (1000 * ((timestamps_segment[i] - timestamps_segment[0]) / (timestamps_segment[-1] - timestamps_segment[0])),  # Scaled timestamp
             250 * ((r_segment[i] - min(r_segment)) / (max(r_segment) - min(r_segment))))  # Normalized PPG data
            for i in range(len(r_segment))
        ]

        # Updating the graph
        self.ids.box.canvas.remove(self.line)
        self.ids.box.canvas.add(Color(83 / 255, 214 / 255, 237 / 255))
        self.line = Line(points=plotting_points, width=2)
        self.ids.box.canvas.add(self.line)

    # Starts or stops data recording
    def record_data(self):
        if self.is_recording:
            self.is_recording = False
            self.ids.process_data.text = "Start Recording"
            self.websocket_client.stop()  # Stop WebSocket client
        else:
            self.is_recording = True
            self.ids.process_data.text = "Stop Recording"
            self.websocket_client.is_running = True  # Start WebSocket client
            self.websocket_client.start_websocket_client()

class PulseOx(App):
    def build(self):
        return PulseOxLayout()

if __name__ == '__main__':
    PulseOx().run()
