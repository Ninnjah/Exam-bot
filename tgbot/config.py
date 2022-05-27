from os import getenv
from dataclasses import dataclass


@dataclass
class DbConfig:
    database_url: str


@dataclass
class TgBot:
    token: str
    admin_id: int
    use_redis: bool


@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig


def cast_bool(value: str) -> bool:
    if not value:
        return False
    return value.lower() in ("true", "t", "1", "yes")


def load_config():
    return Config(
        tg_bot=TgBot(
            token=getenv("BOT_TOKEN"),
            admin_id=int(getenv("ADMIN_ID")),
            use_redis=cast_bool(getenv("USE_REDIS")),
        ),
        db=DbConfig(
            database_url=getenv("DATABASE_URL").replace("postgres://", "postgresql+asyncpg://")
        ),
    )
