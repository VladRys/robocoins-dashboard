from telebot.async_telebot import AsyncTeleBot
from app.core.config import Config

if not Config.BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in the environment variables.")

Bot = AsyncTeleBot(Config.BOT_TOKEN)
