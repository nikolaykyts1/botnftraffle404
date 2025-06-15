from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def game_keyboard():
    buttons = [
        [KeyboardButton(text="🎯 Дартс"), KeyboardButton(text="🏀 Баскетбол")],
        [KeyboardButton(text="⚽ Футбол"), KeyboardButton(text="🎰 Казино")],
        [KeyboardButton(text="🎳 Боулинг"), KeyboardButton(text="🎲 Кубик")],
        [KeyboardButton(text="💣 Минер")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)