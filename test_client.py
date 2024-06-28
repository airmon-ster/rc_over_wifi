# Test client that connects to websocket server and reads data

import asyncio
import websockets

async def main():
    uri = "ws://127.0.0.1:8765"
    async with websockets.connect(uri) as websocket:
        while True:
            data = await websocket.recv()
            print(data)

asyncio.run(main())