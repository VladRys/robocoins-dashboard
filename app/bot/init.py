import asyncio
import logging
import sys

from app.bot.bot import Bot
from app.core.logging_setup import BotLogger
from app.bot.handlers.menu import register_menu_handlers

bot_logger = BotLogger(logging.getLogger("bot"), {})

async def run_bot() -> None:
    try:
        await register_menu_handlers(Bot)
    except Exception:
        bot_logger.exception("Error while registering handlers")
    await Bot.polling()


if __name__ == "__main__":
    bot_logger.info("Starting bot...")
    if sys.platform == "win32":
        # Async psycopg does not support Windows' default ProactorEventLoop.
        asyncio.run(run_bot(), loop_factory=asyncio.SelectorEventLoop)
    else:
        asyncio.run(run_bot())
