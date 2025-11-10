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
