import asyncio
import websockets
import os
import tempfile
import openai
import pyttsx3
from pydub import AudioSegment
from dotenv import load_dotenv
import whisper
import io
import sys

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
print("OPENAI_API_KEY:", OPENAI_API_KEY)  # Debug: Should print your actual key
PORT = int(os.getenv("LLM_SERVER_PORT", 8080))

openai.api_key = OPENAI_API_KEY
whisper_model = whisper.load_model("base")  # You can adjust model size for speed/accuracy

async def stt(audio_bytes):
    """Converts received webm audio to WAV and transcribes using Whisper."""
    try:
        # Decode browser (webm/opus) audio to WAV and downsample to 16kHz mono
        audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="webm")
        audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp_wav:
            audio.export(tmp_wav.name, format="wav")
            result = whisper_model.transcribe(tmp_wav.name)
            return result["text"]
    except Exception as e:
        print(f"Audio decode/STT error: {e}")
        return ""

async def llm_chat(prompt):
    print("DEBUG: OPENAI_API_KEY =", OPENAI_API_KEY)

    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    response = await asyncio.to_thread(
        client.chat.completions.create,
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    assistant_reply = response.choices[0].message.content
    return assistant_reply

async def text_to_speech(text):
    """Synthesizes assistant text reply to speech (.wav) and returns bytes."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
        engine = pyttsx3.init()
        engine.save_to_file(text, tf.name)
        engine.runAndWait()
        tf.seek(0)
        with open(tf.name, "rb") as rf:
            audio_bytes = rf.read()
        os.unlink(tf.name)
        return audio_bytes

async def handle_call(websocket):
    audio_buffer = b""

    while True:
        try:
            data = await websocket.recv()
            print(f"Received data: type={type(data)}, repr={repr(data)[:100]}")
            if isinstance(data, str) and data == "__END__":
                print(f"Received __END__. Final buffer length: {len(audio_buffer)}")
                try:
                    with open("received_audio_debug.webm", "wb") as f:
                        f.write(audio_buffer)
                    print(f"Wrote debug file ({len(audio_buffer)} bytes)")
                except Exception as e:
                    print(f"File write error: {e}")
                transcript = await stt(audio_buffer)
                print(f"Transcript: {transcript}")
                if not transcript.strip():
                    await websocket.send("🤖 Could not transcribe")
                    audio_buffer = b""
                    continue
                assistant_reply = await llm_chat(transcript)
                print(f"Assistant reply: {assistant_reply}")
                tts_audio = await text_to_speech(assistant_reply)
                await websocket.send(tts_audio)
                audio_buffer = b""
            elif isinstance(data, (bytes, bytearray)):
                print(f"Received chunk: {len(data)} bytes")
                audio_buffer += data
            else:
                print(f"Non-str/bytes data: {type(data)}")
        except websockets.ConnectionClosed:
           print("Client disconnected.")
           return

        except Exception as e:
          import traceback
          print(f"Error during call: {e}")
          traceback.print_exc()
          try:
             await websocket.send("🤖 Internal error")
          except Exception as send_error:
            print(f"Error sending internal error message: {send_error}")
          return
async def main():
    print(f"LLM Voice server running on ws://localhost:{PORT}")
    async with websockets.serve(handle_call, "0.0.0.0", PORT, max_size=1024*1024*5):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())

