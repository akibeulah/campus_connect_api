from django.db import models

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone


class UserManager(BaseUserManager):

    def create_user(self, username, email, password=None, **other_fields):
        if username is None:
            raise TypeError('User must have unique user ids, I.E.: registration numbers, matriculation numbers, '
                            'phone numbers, e.t.c')
        if email is None:
            raise TypeError('Users must have a unique email.')

        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, username, email, password, **other_fields):
        """
        Create and return a `User` with superuser (admin) permissions.
        """
        if password is None:
            raise TypeError('Superusers must have a password.')
        if email is None:
            raise TypeError('Superusers must have an email.')
        if username is None:
            raise TypeError('Superusers must have an username.')

        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_admin = True
        user.is_vendor = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(db_index=True, max_length=255, unique=True)
    email = models.EmailField(db_index=True, unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_vendor = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    biometrics_auth = models.BooleanField(default=True)
    biometrics_enabled = models.BooleanField(default=True)
    biometrics_password = models.CharField(max_length=255, blank=True, null=True)
    rfid_auth = models.BooleanField(default=True)
    rfid_auth_enabled = models.BooleanField(default=True)
    rfid_auth_id = models.CharField(max_length=255, blank=True, null=True)
    rfid_auth_pin = models.CharField(max_length=255, blank=True, null=True)
    rfid_auth_attempts = models.IntegerField(default=0, blank=True, null=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    objects = UserManager()

    def __str__(self):
        return f"{self.username}"
