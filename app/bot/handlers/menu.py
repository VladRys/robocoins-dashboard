from app.bot.handlers.base import Handler
from telebot.async_telebot import AsyncTeleBot
from telebot.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LinkPreviewOptions,
    Message,
)
from app.core.database import SessionLocal
from app.repositories.telegram_link import (
    TelegramAccountAlreadyLinkedError,
    TelegramLinkRepository,
)
from app.services.telegram_link import TelegramLinkService


START_MESSAGE = (
    "<b>👋 Привіт, {name}!</b>\n\n"
    "Це бот <b>RoboCoins</b> — тут ти зможеш бути в курсі всього важливого "
    "для свого навчання.\n\n"
    "🔗 <b>Прив’яжи свій акаунт RoboCoins</b>, щоб бот міг надсилати тобі "
    "повідомлення та новини, а ще допомагати проходити щоденні завдання "
    "й користуватися іншими можливостями.\n\n"
    "Натисни кнопку нижче, щоб перейти на сайт і почати."
)


def make_start_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(
            text="🔗 Прив’язати акаунт RoboCoins",
            url="https://robocoins.tech",
            style="success",
        )
    )
    return keyboard

class StartMenuHandler(Handler):
    def __init__(self, bot: AsyncTeleBot):
        self.bot = bot

    async def handle(self, *args, **kwargs):
        @self.bot.message_handler(commands=["start"])
        async def start_command(message: Message):
            parts = (message.text or "").split(maxsplit=1)
            if len(parts) == 2:
                async with SessionLocal() as session:
                    link_service = TelegramLinkService(TelegramLinkRepository(session))
                    try:
                        result = await link_service.consume_link(
                            parts[1], message.from_user.id
                        )
                    except TelegramAccountAlreadyLinkedError:
                        result = "telegram_already_linked"

                responses = {
                    "linked": "✅ Telegram прив’язано до твого акаунта RoboCoins! Тепер бот зможе надсилати тобі важливі повідомлення.",
                    "already_linked": "✅ Цей Telegram уже прив’язано до твого акаунта RoboCoins.",
                    "account_already_linked": "⚠️ До цього акаунта RoboCoins уже прив’язаний інший Telegram. Спочатку відв’яжи його в налаштуваннях акаунта.",
                    "telegram_already_linked": "⚠️ Цей Telegram уже прив’язаний до іншого акаунта RoboCoins.",
                    "expired": "⌛ Посилання застаріло. Створи нове в налаштуваннях RoboCoins.",
                    "invalid": "⚠️ Посилання недійсне або вже використане. Створи нове в налаштуваннях RoboCoins.",
                }
                await self.bot.reply_to(message, responses[result])
                return

            name = message.from_user.first_name or "друже"
            name = (
                name.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )
            await self.bot.reply_to(
                message,
                START_MESSAGE.format(name=name),
                parse_mode="HTML",
                reply_markup=make_start_keyboard(),
                link_preview_options=LinkPreviewOptions(is_disabled=True),
            )

async def register_menu_handlers(bot: AsyncTeleBot):
    start_menu_handler = StartMenuHandler(bot)
    await start_menu_handler.handle()
