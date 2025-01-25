from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import datetime
import aiohttp
from services.database.using_data import get_all_users
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from hanlers import chat
from services import logs
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    global session
    session = aiohttp.ClientSession()
    yield

    await session.close()


app = FastAPI(lifespan=lifespan)

users = {}
api_history = []

templates = Jinja2Templates(directory="sandbox/templates")

session = None

async def get_session():
    global session
    if session is None:
        session = aiohttp.ClientSession()
    return session


async def run_fastapi():
    import uvicorn
    config = uvicorn.Config(app, host="0.0.0.0", port=8001)
    server = uvicorn.Server(config)
    try:
        await server.serve()
    finally:
        global session
        if session:
            await session.close()
            session = None

# Логирование запросов
@app.middleware("http")
async def log_requests(request, call_next):
    start_time = datetime.datetime.now()
    response = await call_next(request)
    end_time = datetime.datetime.now()
    
    api_history.append({
        "endpoint": request.url.path,
        "method": request.method,
        "timestamp": start_time,
        "duration": (end_time - start_time).total_seconds()
    })
    return response

# Получение списка пользователей
@app.get("/users")
async def get_users():
    users = await get_all_users()
    return {
        "users": [
            {
                "user_id": user.user_id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "created_at": user.created_at.isoformat()
            }
            for user in users
        ]
    }

# Получение истории запросов
@app.get("/history")
async def get_api_history():
    return api_history


@app.post("/message_answer")
async def send_message_endpoint(http_message: list):
    try:
        # Проверяем существование чата перед отправкой
        users = await get_all_users()
        user_exists = any(User.user_id == http_message.chat_id for User in users)
        
        if not user_exists:
            return {"status": "error", "message": "Такого пользователя нет"}

        await chat.send_telegram_message(
            chat_id=http_message.chat_id,
            text=http_message.message
        )
        return {"status": "success", "message": "Сообщение успешно отправлено"}
    except Exception as e:
        await logs.logs_bot("error", f"Error sending message: {e}")
        return {"status": "error", "message": "Ошибка при отправке сообщения"}


@app.get("/send_message", response_class=HTMLResponse)
async def show_form(request: Request):
    return templates.TemplateResponse("send_message.html", {"request": request})

@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse(
        "send_message.html",
        {"request": request, "error": str(exc.detail) if hasattr(exc, 'detail') else "Страница не найдена"},
        status_code=404
    )
