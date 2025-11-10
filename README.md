# Live Voice Assistant

## Overview

This project enables real-time voice interaction with an AI assistant using:
- **Speech-to-Text (STT)**: Whisper (by OpenAI)
- **LLM Response**: OpenAI GPT (via API)
- **Text-to-Speech (TTS)**: pyttsx3, or a plugin of your choice

It is designed for "live calls": you speak, and the AI bot replies *via voice*, not just text.

---

## How it Works

1. **Frontend**
   - Captures microphone audio from the user (web app).
   - Streams audio (usually as WebM/Opus chunks) over a WebSocket to the backend.

2. **Backend**
   - Receives audio chunks and buffers them until an "__END__" command.
   - Converts (decodes) and transcribes the full audio to text using the Whisper model.
   - Sends the transcript as a prompt to OpenAI's LLMs via API.
   - Receives model-generated text (the bot’s reply).
   - Synthesizes the reply as speech audio (.wav) using TTS.
   - Streams the audio response back over WebSocket.

3. **Frontend**
   - Plays the received audio reply to the user, creating a "human-like" dialogue.

---

## Live vs Text Mode

- **Live Mode:** The user hears the bot reply via audio, matching the live voice call experience. The backend sends synthesized speech.
- **Text Mode (for debugging):** The backend could also send back plain text replies, but in **live calls**, you want a voice response.

---

## Requirements

- Python 3.8+
- Docker (recommended for backend)
- OpenAI Whisper library (`pip install whisper`)
- OpenAI Python SDK (`pip install openai`)
- pyttsx3 (`pip install pyttsx3`)
- pydub (`pip install pydub`)
- ffmpeg (on system, for audio decoding)
- Frontend with microphone capture and WebSocket support (simple HTML/JS app)

---

## Usage

### 1. Build & Run Backend

```bash
docker build -t llm_voice_server .
docker run -p 8080:8080 --env OPENAI_API_KEY=your_key llm_voice_server
```

### 2. Start Frontend

Serve your `index.html`/`app.js` with an HTTP server (e.g.):
```bash
python3 -m http.server 8081
```

### 3. Make a Call

- Open your web app.
- Press "Start Live Call" and speak.
- Press "End Call."
- Bot replies **with voice**, not just text!

---

## How the Bot Responds in Live Calls

1. **User speaks in browser app.**
2. **Frontend streams audio to backend over WebSocket.**
3. **Backend receives "__END__", transcribes audio, gets AI reply, synthesizes reply to voice, sends audio reply back.**
4. **Frontend receives audio reply and plays it to user—bot "talks back" in real-time.**

> This means **the user gets an audio message as a reply, not just text.**  


## Troubleshooting

- "🤖 Internal error" == check backend logs, usually quota/billing/API bugs.
- Check billing status at [OpenAI Platform](https://platform.openai.com/account/billing).







Project structure 

telegram-voice-bot/
├── bot/
│   ├── bot.py
│   ├── websocket_client.py
│   ├── requirements.txt
├── mini_app/
│   ├── index.html
│   ├── app.js
│   ├── styles.css
├── llm_server/
│   ├── server.py
│   ├── requirements.txt
├── README.md
└── .env

1. Prepare environment variables
Create a .env file in the root folder with:

text
BOT_TOKEN=your_telegram_bot_token_here
WS_SERVER_URL=wss://your-llm-websocket-server.com
OPENAI_API_KEY=your_openai_api_key


2. Create and activate virtual environments
   For bot:-
   cd bot
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

   For llm_server:-
   cd ../llm_server
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt


3. Running the Bot
Start your Telegram bot:-

cd bot
source venv/bin/activate
python bot.py


4. Running the WebSocket Server
Start the backend (LLM server):-

cd llm_server
source venv/bin/activate
python server.py
