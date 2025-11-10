import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from telegram import Update
from telegram.ext import ContextTypes
import asyncio
from websocket_client import get_llm_response

env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
print("Loading dotenv from:", env_path)
load_dotenv(dotenv_path=env_path)
BOT_TOKEN = os.getenv("BOT_TOKEN")
print("Loaded BOT_TOKEN:", BOT_TOKEN)   # Debug: Should print your actual token

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! Send me a voice message and I'll reply with the assistant's synthesized voice."
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"You said: {update.message.text}")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voice = update.message.voice
    file = await context.bot.get_file(voice.file_id)
    file_path = f"{voice.file_id}.ogg"
    await file.download_to_drive(file_path)

    with open(file_path, "rb") as f:
        audio_data = f.read()

    llm_reply_audio = await get_llm_response(audio_data)
    await update.message.reply_voice(llm_reply_audio)

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    application.run_polling()

if __name__ == "__main__":
    main()