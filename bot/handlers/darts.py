import random
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

darts_router = Router()

@darts_router.message(Command("darts"))
async def darts_game(message: Message):
    points = random.randint(0, 60)  # Максимум очков за бросок в дартс 60
    await message.answer(f"Ты бросил дротик и получил {points} очков!")