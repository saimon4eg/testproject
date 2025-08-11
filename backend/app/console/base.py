from typing import Coroutine, Optional
from logging.config import dictConfig

from asyncio import get_event_loop
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.settings import DATABASE_URL
from app.configure import configure


class ConsoleCommand:

    def __init__(self):
        self.db_session: Optional[AsyncSession] = None

    def __call__(self, *args, **kwargs):
        self._configure()
        self._run_coroutine(self._execute())

    async def execute(self):
        raise NotImplementedError

    def _configure(self):
        configure()

    async def _execute(self):
        await self.execute()

    @staticmethod
    def _run_coroutine(coroutine: Coroutine):
        loop = get_event_loop()
        loop.run_until_complete(coroutine)
