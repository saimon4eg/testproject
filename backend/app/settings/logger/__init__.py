config = {
    'disable_existing_loggers': False,  # Не отключаем существующие логгеры
    'version': 1,  # Версия схемы конфигурации
    'formatters': {
        'full': {
            # Полный формат логов: время | уровень | модуль:строка - сообщение
            'format': '%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)s - %(message)s'
        },
    },
    'handlers': {
        'console': {
            'formatter': 'full',  # Используем полный формат
            'class': 'logging.StreamHandler',  # Вывод в консоль
        },
    },
    'loggers': {
        '': {  # Корневой логгер для всех модулей
            'handlers': ['console'],  # Используем консольный обработчик
        },
    },
}
