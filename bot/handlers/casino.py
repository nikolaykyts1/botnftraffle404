import random
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

casino_router = Router()

@casino_router.message(Command("casino"))
async def casino_game(message: Message):
    symbols = ["🍒", "🍋", "🍊", "⭐", "7️⃣"]
    result = [random.choice(symbols) for _ in range(3)]
    text = " | ".join(result)
    if len(set(result)) == 1:
        await message.answer(f"Выпало: {text}\nПоздравляем! Джекпот!")
    else:
        await message.answer(f"Выпало: {text}\nПопробуй еще раз!")