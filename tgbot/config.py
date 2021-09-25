import configparser
from dataclasses import dataclass


@dataclass
class DbConfig:
    host: str
    password: str
    user: str
    database: str


@dataclass
class TgBot:
    token: str
    support_chat_id: int
    use_redis: bool
    enable_metrics: bool


@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig


def cast_bool(value: str) -> bool:
    if not value:
        return False
    return value.lower() in ("true", "t", "1", "yes")


def load_config(path: str):
    config = configparser.ConfigParser()
    config.read(path)

    tg_bot = config["tg_bot"]

    return Config(
        tg_bot=TgBot(
            token=tg_bot["token"],
            support_chat_id=int(tg_bot["support_chat_id"]),
            use_redis=cast_bool(tg_bot.get("use_redis")),
            enable_metrics=cast_bool(tg_bot.get("enable_metrics")),
        ),
        db=DbConfig(**config["db"])
    )
