from aiogram import Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Command
import random
from db import increment_stat

increment_stat(callback.from_user.id, "miner_wins")


miner_router = Router()

SIZE = 10
BOMBS = 10

class MinerStates(StatesGroup):
    playing = State()

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

mode_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="🚩 Флажки", callback_data="mode_flag"),
        InlineKeyboardButton(text="📂 Открывать", callback_data="mode_open"),
    ]
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

def check_win(board, flags):
    bomb_positions = {(i, j) for i in range(SIZE) for j in range(SIZE) if board[i][j] == -1}
    return bomb_positions == flags

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
    await message.answer("Игра Минёр! Поле 10×10. Режим: Открытие клеток.", reply_markup=mode_keyboard)
    await message.answer("Поле:", reply_markup=get_keyboard(await state.get_data()))

@miner_router.callback_query(lambda c: c.data in ["mode_flag", "mode_open"])
async def change_mode(callback: CallbackQuery, state: FSMContext):
    mode = "flag" if callback.data == "mode_flag" else "open"
    await state.update_data(mode=mode)
    await callback.answer(f"Режим: {'Флажки' if mode == 'flag' else 'Открытие'}")

@miner_router.callback_query(lambda c: c.data.startswith("cell_"))
async def handle_cell(callback: CallbackQuery, state: FSMContext):
    _, x, y = callback.data.split("_")
    x, y = int(x), int(y)
    data = await state.get_data()
    board = data["board"]
    opened = data["opened"]
    flags = data["flags"]
    mode = data.get("mode", "open")

    if mode == "flag":
        if (x, y) in opened:
            await callback.answer("Клетка уже открыта")
        elif (x, y) in flags:
            flags.remove((x, y))
            await callback.answer("Флажок снят")
        else:
            flags.add((x, y))
            await callback.answer("Флажок поставлен")
    else:
        if (x, y) in flags:
            await callback.answer("Снимите флажок, чтобы открыть")
        elif board[x][y] == -1:
            opened.add((x, y))
            await state.update_data(opened=opened, flags=flags)
            restart_kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔁 Играть заново", callback_data="restart_miner")]
            ])
            await callback.message.edit_text("💥 Вы наступили на бомбу! Игра окончена.", reply_markup=restart_kb)
            await state.clear()
            await callback.answer()
            return
        else:
            reveal(board, opened, x, y)
            await callback.answer("Открыто")

        await state.update_data(opened=opened, flags=flags)

        if check_win(board, flags):
            await callback.message.edit_text(
                "🎉 Вы выиграли! Все бомбы были отмечены флажками!\nНажмите ниже, чтобы сыграть снова.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔁 Играть заново", callback_data="restart_miner")]
                ])
            )
            await state.clear()
            await callback.answer()
            return

        await callback.message.edit_reply_markup(reply_markup=get_keyboard(await state.get_data()))

    @miner_router.callback_query(lambda c: c.data == "restart_miner")
    async def restart_game(callback: CallbackQuery, state: FSMContext):
        board = create_board()
        await state.set_state(MinerStates.playing)
        await state.update_data(
            board=board,
            opened=set(),
            flags=set(),
            mode="open"
        )
        await callback.message.edit_text("Игра Минёр! Поле 10×10. Режим: Открытие клеток.", reply_markup=mode_keyboard)
        await callback.message.answer("Поле:", reply_markup=get_keyboard(await state.get_data()))
        await callback.answer("Игра начата заново!")