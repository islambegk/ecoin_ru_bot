import sqlalchemy
from sqlalchemy.ext.asyncio import create_async_engine

from tgbot.db.meta import metadata


async def create_db_pool(user, password, host, database):
    pool = create_async_engine(
        f"postgresql+asyncpg://{user}:{password}@{host}/{database}",
        future=True)
    async with pool.begin() as conn:
        await conn.run_sync(metadata.create_all)
        create_hypertable_query = sqlalchemy.text("SELECT create_hypertable('metrics', 'timestamp', if_not_exists => TRUE);")
        await conn.execute(create_hypertable_query)
    return pool
