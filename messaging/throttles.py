import datetime
import logging

from rest_framework import throttling

from .models import BanUsers


class MessageCreateThrottle(throttling.UserRateThrottle):
    scope = 'user'

    def allow_request(self, request, view):
        ban = BanUsers.objects.filter(user=request.user).first()
        if ban:
            if (datetime.datetime.now() - ban.date_add).minutes > 10:
                ban.delete()
                return True
            else:
                logging.warning('Попытка создания сообщения заблокированным пользователем {request.user.id}')
                return False
        allow = super().allow_request(request, view)
        if not allow:
            logging.warning(f'Превышено максимальное количество запросов пользователем {request.user.id}')
        return allow
