from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart

start_router = Router()

@start_router.message(CommandStart())
async def start_command(message: Message):
    await message.answer("Привет! Я бот с мини-играми. Напиши /games чтобы начать!")
