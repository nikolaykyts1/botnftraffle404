from aiogram import Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Command
import random

miner_router = Router()

SIZE = 10
BOMBS = 10

class MinerStates(StatesGroup):
    playing = State()
    game_over = State()

def create_board():
    board = [[0 for _ in range(SIZE)] for _ in range(SIZE)]
    bombs = 0
    while bombs < BOMBS:
        x, y = random.randint(0, SIZE - 1), random.randint(0, SIZE - 1)
        if board[x][y] == -1:
            continue
        board[x][y] = -1
        bombs += 1
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                nx, ny = x + dx, y + dy
                if 0 <= nx < SIZE and 0 <= ny < SIZE and board[nx][ny] != -1:
                    board[nx][ny] += 1
    return board

def get_keyboard(state_data):
    opened = state_data['opened']
    flags = state_data['flags']
    board = state_data['board']
    keyboard = []
    for i in range(SIZE):
        row = []
        for j in range(SIZE):
            if (i, j) in opened:
                val = board[i][j]
                text = "💣" if val == -1 else (str(val) if val > 0 else "⬜")
            elif (i, j) in flags:
                text = "🚩"
            else:
                text = "⬛"
            row.append(InlineKeyboardButton(text=text, callback_data=f"cell_{i}_{j}"))
        keyboard.append(row)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def reveal(board, opened, x, y):
    if (x, y) in opened:
        return
    opened.add((x, y))
    if board[x][y] == 0:
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < SIZE and 0 <= ny < SIZE:
                    reveal(board, opened, nx, ny)

flag_open_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🚩 Флажок"), KeyboardButton(text="⬜ Открыть")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False,
)

restart_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Играть заново")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

@miner_router.message(Command("miner"))
async def cmd_start_miner(message: Message, state: FSMContext):
    board = create_board()
    await state.set_state(MinerStates.playing)
    await state.update_data(
        board=board,
        opened=set(),
        flags=set(),
        mode="open"
    )
    await message.answer(
        "Минёр! Поле 10×10:\n\nРежим: Открытие клеток.\n"
        "Переключитесь с помощью кнопок ниже.",
        reply_markup=flag_open_keyboard
    )
    await message.answer("Выберите клетку:", reply_markup=get_keyboard(await state.get_data()))

@miner_router.message(lambda message: message.text in ["🚩 Флажок", "⬜ Открыть"])
async def switch_mode(message: Message, state: FSMContext):
    mode = "flag" if message.text == "🚩 Флажок" else "open"
    await state.update_data(mode=mode)
    await message.answer(
        f"Режим переключен на: {'Установка флажков' if mode == 'flag' else 'Открытие клеток'}",
        reply_markup=flag_open_keyboard
    )

@miner_router.callback_query(lambda c: c.data.startswith("cell_"))
async def handle_cell(callback: CallbackQuery, state: FSMContext):
    _, x, y = callback.data.split("_")
    x, y = int(x), int(y)
    data = await state.get_data()
    board = data["board"]
    opened = data["opened"]
    flags = data["flags"]
    mode = data["mode"]

    if mode == "flag":
        if (x, y) in opened:
            await callback.answer("Клетка уже открыта")
        elif (x, y) in flags:
            flags.remove((x, y))
        else:
            flags.add((x, y))
    else:  # open mode
        if (x, y) in flags:
            await callback.answer("Снимите флажок, чтобы открыть клетку")
            return
        elif board[x][y] == -1:
            opened.add((x, y))
            await state.update_data(opened=opened)
            await callback.message.edit_text("💥 Вы проиграли!", reply_markup=get_keyboard(data))
            await callback.message.answer("Хотите сыграть заново?", reply_markup=restart_keyboard)
            await state.set_state(MinerStates.game_over)
            await callback.answer()
            return
        else:
            reveal(board, opened, x, y)

    await state.update_data(opened=opened, flags=flags)

        # Проверка победы: выиграл, если все бомбы отмечены флажками, и открыты все остальные клетки
    bombs = {(i, j) for i in range(SIZE) for j in range(SIZE) if board[i][j] == -1}
    all_flags_correct = bombs == flags
    all_opened_correct = opened.union(flags) == {(i, j) for i in range(SIZE) for j in range(SIZE)}

    if all_flags_correct and all_opened_correct:
        await callback.message.edit_text("🎉 Поздравляем! Вы выиграли!", reply_markup=None)
        await callback.message.answer("Хотите сыграть заново?", reply_markup=restart_keyboard)
        await state.set_state(MinerStates.game_over)
        await callback.answer()
        return

    await callback.message.edit_reply_markup(reply_markup=get_keyboard(await state.get_data()))
    await callback.answer()

@miner_router.message(lambda message: message.text == "Играть заново", state=MinerStates.game_over)
async def restart_game(message: Message, state: FSMContext):
    await cmd_start_miner(message, state)
