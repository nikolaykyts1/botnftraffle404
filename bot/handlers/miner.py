from aiogram import Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Command
import random
from stats import get_user_stats, save_stats
miner_router = Router()

SIZE = 10
BOMBS = 10

class MinerStates(StatesGroup):
    playing = State()

# --- ВАЖНО: Импорт статистики из main.py ---
from main import get_user_stats

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
    opened = set(tuple(cell) for cell in state_data['opened'])
    flags = set(tuple(cell) for cell in state_data['flags'])
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

def get_end_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔁 Новая игра", callback_data="new_miner_game")]
    ])

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

def check_win(board, opened):
    total_cells = SIZE * SIZE
    bomb_cells = sum(row.count(-1) for row in board)
    return len(opened) == total_cells - bomb_cells

@miner_router.message(Command("miner"))
async def cmd_start_miner(message: Message, state: FSMContext):
    board = create_board()
    await state.set_state(MinerStates.playing)
    await state.update_data(
        board=board,
        opened=[],
        flags=[],
        mode="open"
    )
    await message.answer("Режим: Открытие клеток. Переключить — /flag или /open")
    await message.answer("Минёр! Поле 10×10:", reply_markup=get_keyboard(await state.get_data()))

@miner_router.message(Command("flag"))
async def switch_to_flag_mode(message: Message, state: FSMContext):
    data = await state.get_data()
    data["mode"] = "flag"
    await state.update_data(data)
    await message.answer("Режим: Установка флажков.")

@miner_router.message(Command("open"))
async def switch_to_open_mode(message: Message, state: FSMContext):
    data = await state.get_data()
    data["mode"] = "open"
    await state.update_data(data)
    await message.answer("Режим: Открытие клеток.")

@miner_router.callback_query(lambda c: c.data == "new_miner_game")
async def restart_game(callback: CallbackQuery, state: FSMContext):
    board = create_board()
    await state.set_state(MinerStates.playing)
    await state.update_data(
        board=board,
        opened=[],
        flags=[],
        mode="open"
    )
    await callback.message.edit_text("Режим: Открытие клеток. Переключить — /flag или /open")
    await callback.message.answer("Минёр! Поле 10×10:", reply_markup=get_keyboard(await state.get_data()))
    await callback.answer()
@miner_router.callback_query(lambda c: c.data.startswith("cell_"))
async def handle_cell(callback: CallbackQuery, state: FSMContext):
    _, x, y = callback.data.split("_")
    x, y = int(x), int(y)
    data = await state.get_data()
    board = data["board"]
    opened = set(tuple(cell) for cell in data["opened"])
    flags = set(tuple(cell) for cell in data["flags"])
    mode = data["mode"]

    if mode == "flag":
        if (x, y) in opened:
            await callback.answer("Клетка уже открыта")
        elif (x, y) in flags:
            flags.remove((x, y))
        else:
            flags.add((x, y))
    else:
        if (x, y) in flags:
            await callback.answer("Снимите флажок, чтобы открыть")
            return
        elif board[x][y] == -1:
            opened.add((x, y))
            await state.update_data(opened=list(opened))
            stats = get_user_stats(callback.from_user.id)
            stats["miner"] = max(0, stats["miner"] - 1)
            await callback.message.edit_text("💥 Вы проиграли!", reply_markup=get_end_keyboard())
            await callback.answer()
            return
        else:
            reveal(board, opened, x, y)

    await state.update_data(opened=list(opened), flags=list(flags))

    if check_win(board, opened):
        stats = get_user_stats(callback.from_user.id)
        stats["miner"] += 1
        await callback.message.edit_text("🎉 Победа! Ты открыл все безопасные клетки!", reply_markup=get_end_keyboard())
        await callback.answer()
        return

    await callback.message.edit_reply_markup(reply_markup=get_keyboard(await state.get_data()))
    await callback.answer()