from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import random
from stats import get_user_stats, save_stats
guess_router = Router()

class GuessStates(StatesGroup):
    waiting_for_guess = State()

def get_number_keyboard():
    buttons = [
        [InlineKeyboardButton(text=str(i), callback_data=f"guess_{i}") for i in range(start, start + 5)]
        for start in range(1, 20, 5)
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@guess_router.message(Command("guess"))
async def cmd_guess_start(message: Message, state: FSMContext):
    number = random.randint(1, 20)
    await state.update_data(number=number)
    await message.answer("🎯 Я загадал число от 1 до 20. Попробуй угадать!", reply_markup=get_number_keyboard())
    await state.set_state(GuessStates.waiting_for_guess)

@guess_router.callback_query(lambda c: c.data.startswith("guess_"))
async def handle_guess(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    target_number = data.get("number")

    try:
        user_guess = int(callback.data.replace("guess_", ""))
    except ValueError:
        await callback.message.answer("Ошибка. Пожалуйста, выбери число.")
        return

    if user_guess == target_number:
        await callback.message.answer(f"🎉 Поздравляю! Ты угадал число {target_number}!")
        await state.clear()
    elif user_guess < target_number:
        await callback.message.answer("📈 Загаданное число больше.")
    else:
        await callback.message.answer("📉 Загаданное число меньше.")

    await callback.answer()