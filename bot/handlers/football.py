import random
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

football_router = Router()

@football_router.message(Command("football"))
async def football_game(message: Message):
    scored = random.choice([True, False])
    if scored:
        await message.answer("Гооол! Ты забил пенальти!")
    else:
        await message.answer("Мимо! Попробуй еще раз.")