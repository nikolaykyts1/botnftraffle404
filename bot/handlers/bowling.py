import random
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

bowling_router = Router()

@bowling_router.message(Command("bowling"))
async def bowling_game(message: Message):
    pins = random.randint(0, 10)
    await message.answer(f"Ты сбил {pins} кеглей!")