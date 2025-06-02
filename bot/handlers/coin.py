from aiogram import Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
import random
from stats import get_user_stats, save_stats
coin_router = Router()

def get_coin_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Орёл 🦅", callback_data="coin_heads")],
        [InlineKeyboardButton(text="Решка 🪙", callback_data="coin_tails")]
    ])

@coin_router.message(Command("coin"))
async def cmd_coin(message: Message):
    await message.answer("🪙 Орёл или Решка? Сделай выбор:", reply_markup=get_coin_keyboard())

@coin_router.callback_query(lambda c: c.data.startswith("coin_"))
async def handle_coin(callback: CallbackQuery):
    user_choice = callback.data.split("_")[1]
    result = random.choice(["heads", "tails"])

    user_text = "Орёл 🦅" if user_choice == "heads" else "Решка 🪙"
    result_text = "Орёл 🦅" if result == "heads" else "Решка 🪙"

    if user_choice == result:
        response = f"🎉 Победа!\nТы выбрал: {user_text}\nВыпало: {result_text}"
    else:
        response = f"😢 Проигрыш!\nТы выбрал: {user_text}\nВыпало: {result_text}"

    await callback.message.answer(response)
    await callback.answer()