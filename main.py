# Import assert
import asyncio

# Import Libary aiogram
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from services import Fastapi, logs
# Import all libary
from config.config import settings

from hanlers.common import router as common_router
from sandbox.admins_panel import router_admin

# Импортируем библиотеку httpx
import httpx

async def routers(dp, bot):
    routers = [
        common_router,
        router_admin
    ]

    for router in routers:
        dp.include_router(router)
    await dp.start_polling(bot)

# Start main
async def main() -> None:

   # await init_db()
   # await init_db_globual() #  globul data

    try:
        bot = Bot(token=settings.config.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2))
        dp = Dispatcher(storage=MemoryStorage())
  #  dp.message.middleware.register(throttling_middleware(storage=storage_ulr))
        await bot.delete_webhook(drop_pending_updates=True)

        # Run FastAPI in a separate task
        asyncio.create_task(Fastapi.run_fastapi())

        await logs.logs_bot("info", f"Bot is ready to work")  # sys.stdout
        #start routers
        await routers(dp, bot)

        # Вызов функции send_message после инициализации бота
        await send_message()
    finally:
        # Закрываем сессию бота при завершении
        await bot.session.close()

async def send_message():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/send-message",
            json={"user_id": 123, "message": "Привет, это тестовое сообщение!"}
        )
        print(response.json())

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as Error:
        asyncio.run(logs.logs_bot("error", f"Bot work off.. {Error}"))