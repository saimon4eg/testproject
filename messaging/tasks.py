import datetime
import logging

from testproject.celery import app
from .models import Message


@app.task
def send_message(message_id):
    try:
        message = Message.objects.get(pk=message_id)
        message.sent = True
        message.updated = datetime.datetime.now()
        message.save()
    except Message.DoesNotExist:
        logging.warning("Не найдено сообщение '%s'" % message_id)
