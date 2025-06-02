import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, BotCommand, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from dotenv import load_dotenv
from stats import load_stats, save_stats, get_user_stats
from handlers.miner import miner_router
from handlers.rps import rps_router
from handlers.guess import guess_router
from handlers.coin import coin_router

# Инициализация
load_dotenv()
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Подключение роутеров
dp.include_router(miner_router)
dp.include_router(rps_router)
dp.include_router(guess_router)
dp.include_router(coin_router)

# Статистика пользователей
user_stats = {}

def get_user_stats(user_id):
    if user_id not in user_stats:
        user_stats[user_id] = {"miner": 0, "coin": 0, "guess": 0, "rps": 0}
    return user_stats[user_id]

def get_game_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧨 Минёр", callback_data="game_miner")],
        [InlineKeyboardButton(text="🪙 Орёл/Решка", callback_data="game_coin")],
        [InlineKeyboardButton(text="🎯 Угадай число", callback_data="game_guess")],
        [InlineKeyboardButton(text="✂️ КНБ", callback_data="game_rps")],
    ])

@dp.message(Command("start"))
async def cmd_start(message: Message):
    name = message.from_user.full_name
    username = message.from_user.username or "нет ника"
    stats = get_user_stats(message.from_user.id)

    text = (
        f"👋 Привет, {name} (@{username})!\n\n"
        f"🎮 Твоя статистика:\n"
        f"🧨 Минёр: {stats['miner']} побед\n"
        f"🪙 Орёл/Решка: {stats['coin']} побед\n"
        f"🎯 Угадай число: {stats['guess']} побед\n"
        f"✂️ КНБ: {stats['rps']} побед\n\n"
        "Выбери игру:"
    )

    await message.answer(text, reply_markup=get_game_menu())

@dp.callback_query(F.data.startswith("game_"))
async def launch_game(callback: CallbackQuery):
    game = callback.data.replace("game_", "")
    commands = {
        "miner": "/miner — начать игру Минёр",
        "coin": "/coin — сыграть в Орёл/Решку",
        "guess": "/guess — начать угадывание числа",
        "rps": "/rps — начать Камень-Ножницы-Бумага"
    }

    if game in commands:
        await callback.message.answer(commands[game])
    await callback.answer()

async def main():
    await bot.set_my_commands([
        BotCommand(command="start", description="Главное меню"),
        BotCommand(command="miner", description="Минёр"),
        BotCommand(command="coin", description="Орёл/Решка"),
        BotCommand(command="guess", description="Угадай число"),
        BotCommand(command="rps", description="Камень-Ножницы-Бумага")
    ])
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())