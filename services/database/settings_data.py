import json, os
from config.config import settings
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

Base = declarative_base()

engine = create_async_engine(settings.config.DATABASE_URL, echo=False) 

# Define User model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# Define Message model
class Message(Base):
    __tablename__ = "message_user"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    text = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    #user = relationship("User", back_populates="messages_user")


# Create async session maker
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Database initialization
async def init_db(): 
    db_dir = os.path.dirname(settings.config.DATABASE_URL.replace('sqlite:///', ''))
    if db_dir and not os.path.exists(db_dir) and 'sandbox/db' not in db_dir:
        os.makedirs(db_dir)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@asynccontextmanager
async def create_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()