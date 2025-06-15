from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

from keyboards.game_keyboard import game_keyboard
from utils.database import update_stats, get_leaderboard
import random
game_router = Router()

games = ["🎯 Дартс", "🏀 Баскетбол", "⚽ Футбол", "🎰 Казино", "🎳 Боулинг", "🎲 Кубик", "💣 Минер"]
@game_router.message(Command("games"))
async def games_menu(message: Message):
    await message.answer("Выберите игру:", reply_markup=game_keyboard())

@game_router.message(Command("leaderboard"))
async def leaderboard(message: Message):
    top = get_leaderboard()
    if not top:
        await message.answer("Рейтинг пока пуст :(")
        return
    text = "🏆 Топ игроков:\n"
    for i, (username, wins, played) in enumerate(top, 1):
        text += f"{i}. {username} — {wins} побед из {played} игр\n"
    await message.answer(text)

@game_router.message()
async def handle_game_choice(message: Message):
    text = message.text.strip() if message.text else ""

    if text == "💣 Минер":
        # Запускаем игру минер — запрашиваем количество мин
        kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="1 мина"), KeyboardButton(text="2 мины"), KeyboardButton(text="3 мины")],
                [KeyboardButton(text="Отмена")]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await message.answer("Выберите количество мин:", reply_markup=kb)
        return

    elif text in ["1 мина", "2 мины", "3 мины"]:
        if text == "Отмена":
            await message.answer("Игра отменена.", reply_markup=game_keyboard())
            return

        try:
            mines = int(text[0])
        except ValueError:
            await message.answer("Пожалуйста, выберите количество мин из предложенных вариантов.")
            return

        field_size = 5
        total_cells = 5
        mines_positions = set(random.sample(range(total_cells), mines))
        safe_cells = total_cells - mines
        won = True if safe_cells > 0 else False

        result_text = f"Минер с {mines} миной(ами)\n"
        result_text += f"Минные позиции: {sorted(mines_positions)} (скрыты от игрока)\n"
        result_text += "Вы выиграли! 🎉" if won else "Вы проиграли. 💥"

        update_stats(message.from_user.id, message.from_user.username or "anon", won)
        await message.answer(result_text, reply_markup=game_keyboard())
        return

    elif text in games:
        # Другие игры
        msg = await message.answer_dice(emoji=text[0])
        value = msg.dice.value
        won = value >= 4
        update_stats(message.from_user.id, message.from_user.username or "anon", won)
        return

    else:
        await message.answer("Выберите игру из меню: /games")