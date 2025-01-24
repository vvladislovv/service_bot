from aiogram import Router, types
from aiogram.filters import CommandStart
from services import MESSAGES, logs
from hanlers import chat

router = Router(name=__name__)

@router.message(CommandStart())
async def command_start(message: types.Message):
    await chat.new_message(message, MESSAGES['ru']['start'], None)