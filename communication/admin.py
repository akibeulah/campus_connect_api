from django.contrib import admin

from communication.models import Message


class MessageAdmin(admin.ModelAdmin):
    model = Message
    search_fields = ('recipient', 'sender',)
    list_display = ('recipient', 'sender', 'message_content', 'received_at', 'read_at', 'created_at',)
    ordering = ('received_at', 'read_at', 'created_at',)


admin.site.register(Message, MessageAdmin)
