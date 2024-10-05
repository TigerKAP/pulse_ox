from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scatter import Scatter
from kivy.graphics import Line, Color
from kivy.uix.label import Label
from kivy.clock import Clock
import numpy as np
import websockets
import asyncio
import threading
from scipy.signal import find_peaks
import traceback

class RealTimePlot(Scatter):
    def __init__(self, **kwargs):
        super(RealTimePlot, self).__init__(**kwargs)
        self.size_hint = (1, 1)
        self.data = []
        self.canvas.add(Color(1, 1, 1))
        self.line = Line(points=[], width=2)
        self.canvas.add(self.line)
        self.update_plot()

    def update_plot(self):
        # Clear the old line
        self.canvas.remove(self.line)
        self.canvas.add(Color(1, 1, 1))
        self.line = Line(points=[], width=2)
        self.canvas.add(self.line)

        if len(self.data) > 1:
            x = np.arange(len(self.data))
            y = np.array(self.data)
            points = [(xi, yi) for xi, yi in zip(x, y)]
            self.line.points = [point for p in points for point in p]

class MyApp(App):
    def build(self):
        self.plot = RealTimePlot()
        self.peaks_label = Label(size_hint_y=None, height=30)
        self.start_websocket_client()
        self.schedule_peak_detection()
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(self.plot)
        layout.add_widget(self.peaks_label)
        return layout

    def add_to_data(self, message):
        def update():
            try:
                values = message.split(',')
                values = [int(val) for val in values]
                print(message)
                self.plot.data.append(values[0])
                if len(self.plot.data) > 1000:
                    self.plot.data.pop(0)
                self.plot.update_plot()
            except ValueError:
                print("Failed to convert message to integers")

        # Schedule the update on the main thread
        Clock.schedule_once(lambda dt: update())

    def start_websocket_client(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        threading.Thread(target=self.websocket_thread, args=(loop,)).start()

    def websocket_thread(self, loop):
        loop.run_until_complete(self.websocket_task(loop))

    async def websocket_task(self, loop):
        uri = "ws://192.168.1.170:80/ws"
        while True:
            try:
                async with websockets.connect(uri, ping_interval=None) as websocket:
                    while True:
                        try:
                            message = await websocket.recv()
                            # Use `Clock.schedule_once` to update the UI on the main thread
                            Clock.schedule_once(lambda dt: self.add_to_data(message))
                        except websockets.ConnectionClosedError as e:
                            print(f"Connection closed with error: {e}")
                            raise e
            except websockets.ConnectionClosedError as e:
                print(f"Reconnecting after connection closed: {e}")
                await asyncio.sleep(5)
            except Exception as e:
                # Print the full traceback of the error
                print(f"Unexpected error: {e}. Retrying...")
                traceback.print_exc()
                await asyncio.sleep(5)

    def schedule_peak_detection(self):
        # Schedule peak detection to run every 1 second
        Clock.schedule_interval(self.detect_peaks, 1)

    def detect_peaks(self, dt):
        if len(self.plot.data) > 1:
            x = np.arange(len(self.plot.data))
            y = np.array(self.plot.data)
            peaks, _ = find_peaks(y)
            peaks_str = ', '.join(map(str, peaks))
            # Update the label with the peak positions
            Clock.schedule_once(lambda dt: self.peaks_label.setter('text')(f"Peaks: {peaks_str}"))

if __name__ == "__main__":
    MyApp().run()
