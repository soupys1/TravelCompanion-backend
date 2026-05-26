import asyncio
import websockets

async def test():
    async with websockets.connect("ws://127.0.0.1:8000/ws") as ws:
        await ws.send("7 days in Japan, medium budget, food and temples")
        while True:
            msg = await ws.recv()
            print(msg, end="", flush=True)
            if msg == "[DONE]":
                break

asyncio.run(test())