import asyncio
import websockets
import os
import tempfile
import numpy as np
import soundfile as sf
import whisper
from dotenv import load_dotenv
import openai

from google.cloud import texttospeech

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PORT = int(os.getenv("LLM_SERVER_PORT", 8080))

openai.api_key = OPENAI_API_KEY
model = whisper.load_model("base")
tts_client = texttospeech.TextToSpeechClient()

async def stt(audio_bytes, sample_rate=16000):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp:
        sf.write(tmp.name, np.frombuffer(audio_bytes, dtype=np.int16), sample_rate)
        result = model.transcribe(tmp.name)
        return result["text"]

async def llm_chat(prompt):
    response = await asyncio.to_thread(
        openai.ChatCompletion.create,
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message["content"]

async def text_to_speech(text):
    # Google Cloud TTS
    input_text = texttospeech.SynthesisInput(text=text)
    voice_params = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16
    )
    response = tts_client.synthesize_speech(
        input=input_text, voice=voice_params, audio_config=audio_config
    )
    return response.audio_content  # bytes

async def handle_call(websocket):
    audio_buffer = b""
    sample_rate = 16000

    while True:
        try:
            data = await websocket.recv()
            if isinstance(data, str) and data == "__END__":
                transcript = await stt(audio_buffer, sample_rate)
                if not transcript.strip():
                    await websocket.send("🤖 Could not transcribe")
                    audio_buffer = b""
                    continue
                print(f"Transcript: {transcript}")
                assistant_reply = await llm_chat(transcript)
                print(f"Assistant reply: {assistant_reply}")
                tts_audio = await text_to_speech(assistant_reply)
                # Send audio back as binary (the frontend must play this)
                await websocket.send(tts_audio)
                audio_buffer = b""
            else:
                audio_buffer += data
        except websockets.ConnectionClosed:
            print("Client disconnected.")
            return

async def main():
    print(f"LLM Voice server running on ws://localhost:{PORT}")
    async with websockets.serve(handle_call, "0.0.0.0", PORT, max_size=1024*1024*5):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())