from sqlalchemy import select, Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from datetime import datetime
import logging
from typing import List, Optional, AsyncGenerator
from contextlib import asynccontextmanager
import json, os

# Create async engine
DATABASE_URL = "sqlite+aiosqlite:///./bot.db"
engine = create_async_engine(DATABASE_URL, echo=True)

# Create declarative base
Base = declarative_base()

#! ПРОВЕРКА НА РАБОТУ БАЗЫ ДАННЫХ + ПОДЛЮЧЕНИЕ

# Define User model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)
    chat_id = Column(Integer, unique=True, nullable=False)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    messages = relationship("Message", back_populates="user")

    @classmethod
    def from_json(cls, json_data: str):
        data = json.loads(json_data)
        return cls(**data)

# Define Message model
class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    text = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="messages")

    @classmethod
    def from_json(cls, json_data: str):
        data = json.loads(json_data)
        return cls(**data)

# Create async session maker
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Database initialization
async def init_db(): #! проверка на то куда сохраняется база данных
    db_dir = os.path.dirname(DATABASE_URL.replace('sqlite:///', ''))
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Get database session
async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

@asynccontextmanager
async def create_session() -> AsyncGenerator[AsyncSession, None]:
    """Creates an asynchronous database session"""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# User operations
async def get_users(json_data: str) -> List[User]: 
    async with create_session() as session:
        try:
            params = json.loads(json_data)
            result = await session.execute("SELECT * FROM users WHERE is_active = true")
            users = result.scalars().all()
            return users
        except Exception as e:
            logging.error(f"Error getting users: {str(e)}")
            return []

async def get_user_by_id(json_data: str) -> Optional[User]:
    async with create_session() as session:
        try:
            params = json.loads(json_data)
            user_id = params.get('user_id')
            result = await session.execute(
                "SELECT * FROM users WHERE user_id = :user_id",
                {"user_id": user_id}
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logging.error(f"Error getting user: {str(e)}")
            return None

async def check_existing_user( user_id: int) -> Optional[User]:
    async with create_session() as session:
        try:
            stmt = select(User).where(User.user_id == user_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logging.error(f"Error checking existing user: {str(e)}")
            return None


async def create_user(json_data: str) -> Optional[User]:
    async with create_session() as session:
        try:
            user_data = json.loads(json_data)
            # Check if user already exists
            existing_user = await check_existing_user(session, user_data['user_id'])
            if existing_user:
                logging.info(f"User with id {user_data['user_id']} already exists")
                return None
                
            user = User(
                user_id=user_data['user_id'],
                chat_id=user_data['chat_id'],
                username=user_data.get('username'),
                first_name=user_data.get('first_name'),
                last_name=user_data.get('last_name')
            )
            session.add(user)
            await session.commit()
            return user
        except Exception as e:
            await session.rollback()
            logging.error(f"Error creating user: {str(e)}")
            return None

# Message operations
async def create_message(json_data: str) -> Optional[Message]:
    async with create_session() as session:
        try:
            message_data = json.loads(json_data)
            message = Message(
                user_id=message_data['user_id'],
                text=message_data['text']
            )
            session.add(message)
            await session.commit()
            return message
        except Exception as e:
            await session.rollback()
            logging.error(f"Error creating message: {str(e)}")
            return None

async def get_user_messages(json_data: str) -> List[Message]:
    async with create_session() as session:
        try:
            params = json.loads(json_data)
            user_id = params.get('user_id')
            result = await session.execute(
                "SELECT * FROM messages WHERE user_id = :user_id ORDER BY created_at DESC",
                {"user_id": user_id}
            )
            return result.scalars().all()
        except Exception as e:
            logging.error(f"Error getting user messages: {str(e)}")
            return []
