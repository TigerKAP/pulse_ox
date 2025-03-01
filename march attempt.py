import asyncio
import websockets
import json

ESP32_WS_URL = "ws://192.168.4.1/ws"
data_log = []

async def receive_data():
    async with websockets.connect(ESP32_WS_URL) as websocket:
        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)

                if len(data.get("red", [])) == 500 and len(data.get("ir", [])) == 500:
                    print("Received 500-element arrays.")
                    data_log.append(data)
                else:
                    print("Warning: Array length mismatch.",
                          "red length:", len(data.get("red", [])), 
                          "ir length:", len(data.get("ir", [])))
            except Exception as e:
                print("Error occurred:", e)

# Run the event loop properly in a standalone script
if __name__ == "__main__":
    asyncio.run(receive_data())
