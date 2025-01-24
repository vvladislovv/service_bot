from datetime import datetime
from dataclasses import dataclass, field
from environs import Env

@dataclass
class Admins:
    admins: list[int] 

@dataclass
class DatabaseConfig:
    dbname: str = 'users_database'
    user: str = 'postgres'
    password: str = 'admin'
    host: str = 'localhost'
    port: int = 5433

@dataclass
class OpenAIConfig:
    api_key: str
    base_url: str = "https://api.proxyapi.ru/openai/v1"

@dataclass
class Config:
    bot_token: str
    openai: OpenAIConfig
    database: DatabaseConfig  
    admins: Admins

@dataclass
class Settings:
    config: Config


def get_settings(path: str = None):
    env = Env()
    env.read_env(path)

    return Settings(
        config=Config(
            bot_token=env.str("TOKEN_BOT"),
            admins=Admins(
                admins=env.list("ADMINS")
            ),
            database=DatabaseConfig(
                dbname=env.str("DB_NAME"),
                user=env.str("DB_USER"),
                password=env.str("DB_PASSWORD"),
                host=env.str("DB_HOST"),
                port=env.int("DB_PORT")
            ),
            openai=OpenAIConfig(
                api_key=env.str("PROXY_API_KEY")
            )
        )
    )


settings = get_settings()