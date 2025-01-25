import json
from .settings_data import User, Message, create_session
from sqlalchemy import select
from typing import List, Optional
from services import logs, convert_to_json

async def get_all_users() -> List[User]: 
    async with create_session() as session:
        try:
            stmt = select(User)
            result = await session.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            await logs.logs_bot("error", f"Error getting users: {str(e)}")
            return []

async def get_user_by_id(json_data: str) -> Optional[User]:
    async with create_session() as session:
        try:
            params = json.loads(json_data)
            user_id = params.get('user_id')
            stmt = select(User).where(User.user_id == user_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            await logs.logs_bot("error", f"Error getting user: {str(e)}")
            return None

async def check_existing_user(user_id: int):
    async with create_session() as session:
        try:
            stmt = select(User).where(User.user_id == user_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            await logs.logs_bot("error", f"Error checking existing user: {str(e)}")
            return None

async def create_entity(user_data: str, entity_type: str):
    async with create_session() as session:
        try:
            json_data = convert_to_json(user_data)
            data = json.loads(json_data)

            if entity_type == "user":
                return await _create_user(data)
            elif entity_type == "message":
                return await _create_message(data)
            else:
                await logs.logs_bot("error", f"Unknown entity type: {entity_type}")
                return None
                
        except Exception as e:
            await session.rollback()
            await logs.logs_bot("error", f"Error creating {entity_type}: {str(e)}")
            return None

async def _create_user(user_data: dict):
    async with create_session() as session:
        existing_user = await check_existing_user(user_data['user_id'])
        if existing_user:
            await logs.logs_bot("info", f"User with id {user_data['user_id']} already exists")
            return None
        
        user = User(
            user_id=user_data['user_id'],
            username=user_data.get('username'),
            first_name=user_data.get('first_name'),
            last_name=user_data.get('last_name')
        )

        session.add(user)
        await session.commit()
        return user

async def _create_message(message_data: dict) -> Optional[Message]:
    async with create_session() as session:
        message = Message(
            user_id=message_data['user_id'],
            text=message_data['text']
        )
        session.add(message)
        await session.commit()
        
        return message

async def get_user_messages(json_data: str) -> List[Message]:
    async with create_session() as session:
        try:
            params = json.loads(json_data)
            user_id = params.get('user_id')
            result = await session.execute(
                select(Message).where(Message.user_id == user_id).order_by(Message.created_at.desc())
            )
            return result.scalars().all()
        except Exception as e:
            await logs.logs_bot("error", f"Error getting user messages: {str(e)}")
            return []