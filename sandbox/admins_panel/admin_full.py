
from aiogram.filters import Command
from aiogram import Router
from aiogram import types
from services import MESSAGES
from hanlers import chat

import os

router = Router(name=__name__)

@router.message(Command("admin"))
async def admin_panel(message: types.Message) -> None:
    if message.from_user.id in list(map(int, os.getenv('ADMINS', '').split(','))):
        await chat.new_message(message, MESSAGES['ru']['admin_msg'], None)
