from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
import random
from stats import get_user_stats, save_stats
rps_router = Router()
from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
import random

rps_router = Router()

# Клавиатура выбора
def rps_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✊ Камень", callback_data="rps_rock"),
            InlineKeyboardButton(text="✋ Бумага", callback_data="rps_paper"),
            InlineKeyboardButton(text="✌️ Ножницы", callback_data="rps_scissors")
        ]
    ])

@rps_router.message(Command("rps"))
async def cmd_rps(message: Message):
    await message.answer(
        "Выберите: камень, ножницы или бумага!",
        reply_markup=rps_keyboard()
    )

@rps_router.callback_query(lambda c: c.data.startswith("rps_"))
async def handle_rps_choice(callback):
    user_choice = callback.data.replace("rps_", "")
    choices = ["rock", "paper", "scissors"]
    bot_choice = random.choice(choices)

    choice_names = {
        "rock": "✊ Камень",
        "paper": "✋ Бумага",
        "scissors": "✌️ Ножницы"
    }

    result_text = get_result(user_choice, bot_choice)

    await callback.message.answer(
        f"Вы выбрали: {choice_names[user_choice]}\n"
        f"Бот выбрал: {choice_names[bot_choice]}\n\n"
        f"{result_text}"
    )
    await callback.answer()

def get_result(user, bot):
    if user == bot:
        return "🔁 Ничья!"
    elif (
        (user == "rock" and bot == "scissors") or
        (user == "scissors" and bot == "paper") or
        (user == "paper" and bot == "rock")
    ):
        return "🎉 Вы победили!"
    else:
        return "😢 Вы проиграли!"