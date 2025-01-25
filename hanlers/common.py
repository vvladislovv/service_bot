from aiogram import Router, types
from aiogram.filters import CommandStart
from services import MESSAGES
from hanlers import chat

from services.database.using_data import create_entity

router = Router(name=__name__)

@router.message(CommandStart())
async def command_start(message: types.Message):
    await chat.new_message(message, MESSAGES['ru']['start'], None)

    user_data = {
        'user_id': message.from_user.id,
        'username': message.from_user.username,
        'first_name': message.from_user.first_name,
        'last_name': message.from_user.last_name
    }

    await create_entity(user_data, "user")
