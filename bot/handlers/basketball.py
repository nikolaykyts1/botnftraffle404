import random
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

basketball_router = Router()

@basketball_router.message(Command("basketball"))
async def basketball_game(message: Message):
    outcomes = [0, 2, 3]  # 0 - промах, 2 или 3 очка
    result = random.choice(outcomes)
    if result == 0:
        await message.answer("Промах! Попробуй еще раз.")
    else:
        await message.answer(f"Ура! Ты забросил {result} очка!")