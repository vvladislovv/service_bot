from dataclasses import dataclass
from environs import Env

@dataclass
class Admins:
    admins: list[int] 

@dataclass
class OpenAIConfig:
    api_key: str
    base_url: str = "https://api.proxyapi.ru/openai/v1"

@dataclass
class Config:
    bot_token: str
    openai: OpenAIConfig

    admins: Admins
    DATABASE_URL: str 

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
            DATABASE_URL=env.str("DATABASE_URL"),

            openai=OpenAIConfig(
                api_key=env.str("PROXY_API_KEY")
            )
        )
    )


settings = get_settings()