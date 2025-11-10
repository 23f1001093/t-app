import os
import asyncio
import websockets
from dotenv import load_dotenv

load_dotenv()
WS_SERVER_URL = os.getenv("WS_SERVER_URL")

async def get_llm_response(audio_bytes):
    async with websockets.connect(WS_SERVER_URL) as ws:
        await ws.send(audio_bytes)
        reply = await ws.recv()
        return reply.decode() if isinstance(reply, bytes) else reply