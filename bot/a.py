from dotenv import load_dotenv
import os

load_dotenv()  # This loads variables from .env into your environment

print("BOT_TOKEN:", os.getenv("BOT_TOKEN"))
