from django.db import models


class Message(models.Model):
    created = models.DateTimeField('Дата создания', auto_now_add=True)
    updated = models.DateTimeField('Дата обновления', auto_now_add=True)
    title = models.CharField('Заголовок', max_length=100, blank=True, default='')
    body = models.TextField('Сообщение', blank=True, default='')
    sender = models.ForeignKey('auth.User', verbose_name='Отправитель', related_name='sender_messages',
                               on_delete=models.CASCADE)
    recipient = models.ForeignKey('auth.User', verbose_name='Получатель', related_name='recipient_messages',
                                  on_delete=models.CASCADE)
    sent = models.BooleanField('Отправлено', default=False)
    read = models.BooleanField('Прочитано', default=False)

    class Meta:
        ordering = ['created']


def message_post_save(sender, instance, **kwargs):
    if not instance.sent:
        from .tasks import send_message
        send_message.delay(instance.pk)


models.signals.post_save.connect(message_post_save, sender=Message)


class BanUsers(models.Model):
    date_add = models.DateTimeField('Дата создания', auto_now_add=True)
    user = models.ForeignKey('auth.User', verbose_name='Заблокированный пользователь', related_name='banusers',
                             on_delete=models.CASCADE)
