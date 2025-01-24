from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardMarkup
from services import logs

async def new_message(message : Message, text : str, keyword : InlineKeyboardMarkup) -> Message:
    try:
        markup = None
        if keyword:
            if isinstance(keyword, (InlineKeyboardMarkup, list)):
                markup = keyword if isinstance(keyword, InlineKeyboardMarkup) else InlineKeyboardMarkup(inline_keyboard=keyword)
            else:
                markup = keyword.as_markup()
                
        return await message.answer(
            text=text,
            parse_mode="Markdown",
            reply_markup=markup
        )
    except Exception as e:
        await logs.logs_bot("error", f"Error in new_message: {e}")


async def update_message(message : Message, text : str, keyword : InlineKeyboardMarkup) -> Message:
    try:
        markup = None
        if keyword:
            if isinstance(keyword, InlineKeyboardMarkup):
                markup = keyword
            elif isinstance(keyword, list):
                markup = InlineKeyboardMarkup(inline_keyboard=keyword)
            else:
                markup = keyword.as_markup()
                
        await message.edit_text(
            text,
            parse_mode="Markdown", 
            reply_markup=markup
        )
    except Exception as error:
        await logs.logs_bot("error", f"Error in update_message: {error}")