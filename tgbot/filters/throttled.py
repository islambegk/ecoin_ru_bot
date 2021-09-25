from aiogram.dispatcher.filters import BoundFilter
from aiogram.dispatcher.handler import ctx_data


class ThrottledFilter(BoundFilter):
    key = "is_throttled"

    async def check(self, _):
        throttled = ctx_data.get()["throttled"]
        return throttled and throttled > 0
