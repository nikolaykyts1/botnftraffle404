from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
import random

from db import increment_stat  # импорт функции для обновления статистики

coin_router = Router()

# Клавиатура для выбора
def coin_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Орёл", callback_data="coin_heads"),
            InlineKeyboardButton(text="Решка", callback_data="coin_tails")
        ]
    ])

@coin_router.message(Command("coin"))
async def start_coin(message: Message):
    await message.answer("🪙 Выберите: Орёл или Решка", reply_markup=coin_keyboard())

@coin_router.callback_query(F.data.startswith("coin_"))
async def coin_result(callback: CallbackQuery):
    user_choice = callback.data.split("_")[1]
    result = random.choice(["heads", "tails"])

    if user_choice == result:
        increment_stat(callback.from_user.id, "coin_wins")
        await callback.message.edit_text(f"🎉 Выпало: {'Орёл' if result == 'heads' else 'Решка'}\nВы выиграли!")
    else:
        await callback.message.edit_text(f"😢 Выпало: {'Орёл' if result == 'heads' else 'Решка'}\nВы проиграли.")

    await callback.answer()