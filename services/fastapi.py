import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import datetime
import aiohttp
from config.config import settings  # Импортируем настройки для получения токена

# Создаем FastAPI приложение
app = FastAPI()

users = {}
api_history = []

class User(BaseModel):
    chat_id: int
    user_id: int  # Добавляем поле user_id

class Message(BaseModel):
    user_id: int
    message: str

# Создаем единую сессию для всего приложения
session = None

async def get_session():
    global session
    if session is None:
        session = aiohttp.ClientSession()
    return session


async def run_fastapi():
    import uvicorn
    config = uvicorn.Config(app, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)
    try:
        await server.serve()
    finally:
        # Закрываем сессию при завершении работы
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
@app.get("/users", response_model=List[User])
async def get_users():
    return list(users.values())

# Получение истории запросов
@app.get("/api-history")
async def get_api_history():
    return api_history

# Отправка сообщения пользователю
@app.post("/send-message")
async def send_message_endpoint(message):
    if message.user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    
    
    return {"status": "success", "message": "Message sent"}

# Добавление нового пользователя
@app.post("/users")
async def add_user(user: User):
    users[user.user_id] = user
    return user