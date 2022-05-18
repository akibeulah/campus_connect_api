from django.db import models
from django.utils import timezone

from user.models import User


class Message(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=False, default=1,
                                  related_name="recipient")
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=False, default=1,
                               related_name="sender")
    message_content = models.TextField(blank=False, null=False)
    received_at = models.DateTimeField(blank=True, null=True)
    read_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def last_50_messages(self):
        return Message.objects.order_by('-created_at').all()[:50]