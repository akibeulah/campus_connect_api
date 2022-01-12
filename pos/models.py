from django.db import models
# from mirage import fields
from django.utils import timezone
from user.models import User


class POS(models.Model):
    UID = models.CharField(db_index=True, max_length=255, unique=True)
    password = models.CharField(max_length=1024)
    token = models.CharField(max_length=1024, null=True)
    is_active = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "POS"
        verbose_name_plural = "POS"

    def __str__(self):
        return self.UID


class Transaction(models.Model):
    AUTH_TYPES = (
        ('SYSTEM', 'system'),
        ('BIOMETRICS', 'biometrics'),
        ('RFID', 'rfid')
    )

    TRANSACTION_TYPES = (
        ('IN', 'in'),
        ('OUT', 'out')
    )

    transaction_type = models.CharField(max_length=255, blank=False, null=False, choices=TRANSACTION_TYPES,
                                        default="OUT")
    transaction_amount = models.CharField(max_length=255, blank=False, null=True)
    transaction_title = models.CharField(max_length=255, blank=False, null=True, default="Error!!!")
    transaction_desc = models.TextField(blank=False, null=True)
    auth_type = models.CharField(max_length=255, blank=False, null=False, choices=AUTH_TYPES, default="BIOMETRICS")
    consumer = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name='consumer')
    vendor = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name='vendor')
    pos = models.ForeignKey(POS, on_delete=models.PROTECT, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
