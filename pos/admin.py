from django.contrib import admin
from django.db import models
from django.forms import Textarea

from pos.models import POS, Transaction


class POSAdmin(admin.ModelAdmin):
    model = POS
    search_fields = ('UID', 'user')
    list_filter = ('is_active',)
    ordering = ('-created_at',)
    list_display = ('UID', 'user', 'password', 'is_active', 'created_at')
    # fieldsets = (
    #     (None, {'fields': ('UID', 'user', 'password', 'is_active', 'created_at', 'password')}),
    #     ('Permissions', {'fields': ('is_active', )})
    # )


class TransactionAdmin(admin.ModelAdmin):
    model = Transaction
    search_fields = ('consumer', 'vendor', 'pos')
    list_filter = ('auth_type', 'transaction_type', 'pos')
    ordering = ('-created_at',)
    list_display = ('transaction_type', 'transaction_amount', 'transaction_desc', 'auth_type', 'consumer', 'vendor',
                  'pos', 'created_at',)


admin.site.register(POS, POSAdmin)
admin.site.register(Transaction, TransactionAdmin)
