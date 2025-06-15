import random
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

dice_router = Router()

@dice_router.message(Command("dice"))
async def dice_game(message: Message):
    roll = random.randint(1, 6)
    await message.answer(f"Выпало число: {roll}")