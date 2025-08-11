from .base import ConsoleCommand
from app.core.database.engine import get_engine
from sqlalchemy import text


class CheckDataBaseConnectionCommand(ConsoleCommand):

    async def execute(self):
        try:
            engine = get_engine()
            async with engine.connect() as conn:
                # Простой запрос для проверки соединения
                await conn.execute(text("SELECT 1"))
            print('success')
        except Exception as e:
            print(f'failure: {e}')
