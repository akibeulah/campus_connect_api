from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db import models
from django.forms import Textarea

from user.models import User


class UserAdminConfig(UserAdmin):
    model = User
    search_fields = ('email', 'username', 'first_name', 'last_name')
    list_filter = ('is_active', 'is_staff', 'is_vendor', 'is_admin')
    ordering = ('-created_at',)
    list_display = (
        'username', 'id', 'email', 'first_name', 'last_name', 'rfid_auth', 'rfid_auth_enabled', 'rfid_auth_id',
        'biometrics_auth', 'biometrics_enabled',
        'is_active', 'is_staff', 'is_vendor', 'is_admin', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('email', 'username', 'first_name', 'last_name', 'password', 'rfid_auth_id', 'rfid_auth_pin')}),
        ('Permissions', {'fields': (
            'is_staff', 'is_active', 'is_vendor', 'is_admin', 'rfid_auth', 'rfid_auth_enabled', 'biometrics_auth',
            'biometrics_enabled',)})
    )
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 20, 'cols': 60})},
    }
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'username', 'first_name', 'last_name', 'password', 'is_vendor', 'is_admin', 'is_active',
                'is_staff')}
         ),
    )


admin.site.register(User, UserAdminConfig)
