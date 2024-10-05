from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scatter import Scatter
from kivy.graphics import Line, Color
from kivy.clock import Clock
import numpy as np
import websockets
import asyncio
import threading

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
        self.start_websocket_client()
        layout = BoxLayout()
        layout.add_widget(self.plot)
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
                print(f"Unexpected error: {e}. Retrying...")
                await asyncio.sleep(5)

if __name__ == "__main__":
    MyApp().run()
