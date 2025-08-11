from asyncio import run, iscoroutinefunction
from functools import wraps


def run_coroutine(func):
    """
    Декоратор для преобразования асинхронных функций в синхронные.
    Автоматически запускает корутины с помощью asyncio.run()
    Если переданная функция не является корутиной, возвращается без изменений.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        """Обертка для запуска асинхронной функции синхронно."""
        return run(func(*args, **kwargs))

    if iscoroutinefunction(func):
        return wrapper
    else:
        return func
