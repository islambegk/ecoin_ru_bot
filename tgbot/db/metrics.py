from sqlalchemy import Table, Column, String, BigInteger, Float
from sqlalchemy.dialects.postgresql import TIMESTAMP

from tgbot.db.meta import metadata


metrics_table = Table(
    "metrics",
    metadata,
    Column("user_id", BigInteger),
    Column("chat_id", String),
    Column("timestamp", TIMESTAMP(timezone=False), nullable=False),
    Column("update_type", String),
    Column("action", String),
    Column("time_delta", Float),
)
