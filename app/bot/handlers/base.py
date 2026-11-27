from abc import ABC, abstractmethod
from telebot.async_telebot import AsyncTeleBot

class Handler(ABC):
    def __init__(self, bot: AsyncTeleBot):
        self.bot = bot
        
    @abstractmethod
    async def handle(self, *args, **kwargs):
        raise NotImplementedError("Subclasses must implement the handle method.")