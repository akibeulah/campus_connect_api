from django.contrib import admin

from pos.models import POS, Transaction, POSHandovers, Remittance


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
    list_display = (
        'transaction_title', 'transaction_type', 'transaction_amount', 'transaction_desc', 'auth_type', 'consumer',
        'vendor',
        'pos', 'created_at',)


class POSHandoversAdmin(admin.ModelAdmin):
    model = POSHandovers
    search_fields = ('vendor',)
    list_filter = ('request_approval',)
    ordering = ('-request_made_at', '-collected_at', '-returned_at', '-updated_at')
    list_display = (
        'request_made_at',
        'request_type',
        'request_desc',
        'request_approval',
        'pos',
        'collected_at',
        'returned_at',
        'updated_at',
    )


class RemittanceAdmin(admin.ModelAdmin):
    model = Remittance
    search_fields = ('vendor',)
    list_filter = ('request_approval',)
    ordering = ('-created_at', '-updated_at')
    list_display = ('vendor',
                    'request_approval',
                    'created_at',
                    'updated_at')


admin.site.register(POS, POSAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(POSHandovers, POSHandoversAdmin)
admin.site.register(Remittance, RemittanceAdmin)
