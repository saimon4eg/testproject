import json
import logging
import asyncio
from typing import Optional, Dict, Any
import aio_pika
from aio_pika.abc import AbstractConnection, AbstractChannel, AbstractQueue
from app.settings import RABBITMQ_URL
from app.utils import Singleton

logger = logging.getLogger(__name__)


class RabbitMQService(metaclass=Singleton):
    """Сервис для работы с RabbitMQ"""
    
    def __init__(self):
        self._connection: Optional[AbstractConnection] = None
        self._channel: Optional[AbstractChannel] = None
        self._queues: Dict[str, AbstractQueue] = {}
    
    async def connect(self):
        """Подключение к RabbitMQ"""

        if not self._connection or self._connection.is_closed:
            try:
                self._connection = await aio_pika.connect_robust(
                    RABBITMQ_URL,
                    client_properties={"connection_name": "testproject_backend"}
                )
                self._channel = await self._connection.channel()
                await self._channel.set_qos(prefetch_count=10)
                logger.info("Подключение к RabbitMQ установлено")
            except Exception as e:
                logger.error(f"Ошибка подключения к RabbitMQ: {e}")
                raise
    
    async def declare_queue(self, queue_name: str, durable: bool = True) -> AbstractQueue:
        """Объявление очереди"""

        await self.connect()
        
        if queue_name not in self._queues:
            queue = await self._channel.declare_queue(
                queue_name, 
                durable=durable,
                arguments={"x-message-ttl": 3600000}  # TTL 1 час
            )
            self._queues[queue_name] = queue
            logger.info(f"Очередь {queue_name} объявлена")
        
        return self._queues[queue_name]
    
    async def publish_message(self, queue_name: str, message: Dict[str, Any], priority: int = 0):
        """Отправка сообщения в очередь"""

        try:
            await self.declare_queue(queue_name)
            
            message_body = json.dumps(message, ensure_ascii=False).encode('utf-8')
            
            await self._channel.default_exchange.publish(
                aio_pika.Message(
                    message_body,
                    priority=priority,
                    content_type='application/json',
                    content_encoding='utf-8',
                    headers={
                        'created_at': asyncio.get_event_loop().time(),
                        'message_type': message.get('type', 'unknown')
                    }
                ),
                routing_key=queue_name
            )
            
            logger.info(f"Сообщение отправлено в очередь {queue_name}: {message.get('type', 'unknown')}")
            
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения в RabbitMQ: {e}")
            raise
    
    async def consume_messages(self, queue_name: str, callback, auto_ack: bool = False):
        """Подписка на сообщения из очереди"""

        try:
            queue = await self.declare_queue(queue_name)
            
            async def message_handler(message: aio_pika.IncomingMessage):
                async with message.process(requeue=True):
                    try:
                        body = json.loads(message.body.decode('utf-8'))
                        await callback(body, message)
                        logger.debug(f"Сообщение обработано из очереди {queue_name}")
                    except json.JSONDecodeError as e:
                        logger.error(f"Ошибка декодирования JSON: {e}")
                        raise
                    except Exception as e:
                        logger.error(f"Ошибка обработки сообщения: {e}")
                        raise
            
            await queue.consume(message_handler, no_ack=auto_ack)
            logger.info(f"Подписка на очередь {queue_name} активна")
            
        except Exception as e:
            logger.error(f"Ошибка при подписке на очередь {queue_name}: {e}")
            raise
    
    async def close(self):
        """Закрытие подключения"""
        if self._connection and not self._connection.is_closed:
            await self._connection.close()
            logger.info("Подключение к RabbitMQ закрыто")
