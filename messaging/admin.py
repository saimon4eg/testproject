from django.contrib import admin

from .models import Message


class MessageAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'updated')


admin.site.register(Message, MessageAdmin)
