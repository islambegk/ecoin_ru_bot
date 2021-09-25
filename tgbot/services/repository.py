from typing import Union

from aioredis import Redis
from aiogram.utils.json import json

from tgbot.db.metrics import metrics_table


class Repo:
    def __init__(self, db_conn, redis_conn: Redis):  # db_conn,
        self._db_conn = db_conn
        self._redis_conn = redis_conn
        self._redis_pipeline = self._redis_conn.pipeline(transaction=True)

    async def get_menu_message_id(self, user_id: int, chat_id: Union[int, str]):
        menu_message_id = await self._redis_conn.get(f"menu_message_id:{chat_id}:{user_id}")
        if menu_message_id:
            return int(menu_message_id)

    async def set_menu_message_id(self, menu_message_id: int, user_id: int, chat_id: Union[int, str], as_pipeline: bool = False):
        redis_key = f"menu_message_id:{chat_id}:{user_id}"
        if as_pipeline:
            return await self._redis_pipeline.set(redis_key, menu_message_id).execute()
        return await self._redis_conn.set(redis_key, menu_message_id)

    async def watch_menu_message_id(self, user_id: int, chat_id: Union[int, str]):
        await self._redis_pipeline.watch(f"menu_message_id:{chat_id}:{user_id}")
        self._redis_pipeline.multi()

    async def get_question_data(self, question_message_id: int):
        data_json = await self._redis_conn.get(f"question:{question_message_id}")
        return json.loads(data_json)

    async def set_question_data(self, question_message_id: int, data):
        return await self._redis_conn.set(f"question:{question_message_id}", json.dumps(data))

    async def get_banned(self, user_id: int):
        is_banned = await self._redis_conn.get(f"banned:{user_id}")
        return int(is_banned) if is_banned else 0

    async def set_banned(self, is_banned: int, user_id: int):
        return await self._redis_conn.set(f"banned:{user_id}", is_banned)

    async def post_metrics(self, metrics_data):
        await self._db_conn.execute(metrics_table.insert().values(**metrics_data))
        await self._db_conn.commit()

    

