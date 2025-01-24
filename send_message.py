import httpx
import asyncio

async def send_message():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/send-message",
            json={"user_id": 123, "message": "Привет, это тестовое сообщение!"}
        )
        print(response.json())

# Для запуска функции
if __name__ == "__main__":
    asyncio.run(send_message()) 