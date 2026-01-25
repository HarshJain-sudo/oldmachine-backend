"""
User models for olmachine_users app.
"""

import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from django.conf import settings


class UserManager(BaseUserManager):
    """Custom user manager."""

    def create_user(self, phone_number=None, country_code=None, username=None, **extra_fields):
        """
        Create and save a regular user.

        Args:
            phone_number: User phone number (optional for admin users)
            country_code: Country code (optional for admin users)
            username: Username (for admin users)
            **extra_fields: Additional user fields

        Returns:
            User: Created user instance
        """
        if not phone_number and not username:
            raise ValueError('Either phone_number or username is required')

        user = self.model(
            phone_number=phone_number,
            country_code=country_code,
            username=username,
            **extra_fields
        )
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        """
        Create and save a superuser.

        Args:
            username: Username for superuser
            password: Password for superuser
            **extra_fields: Additional user fields

        Returns:
            User: Created superuser instance
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        if not username:
            raise ValueError('Username is required for superuser')

        user = self.model(username=username, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    """Custom user model using phone number or username authentication."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(
        max_length=150,
        unique=True,
        null=True,
        blank=True,
        help_text="Username for admin users"
    )
    phone_number = models.CharField(
        max_length=15,
        unique=True,
        null=True,
        blank=True,
        help_text="Phone number for regular users"
    )
    country_code = models.CharField(
        max_length=5,
        null=True,
        blank=True,
        help_text="Country code for phone number"
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        """Meta options for User model."""

        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(username__isnull=False) |
                    models.Q(phone_number__isnull=False)
                ),
                name='user_must_have_username_or_phone'
            )
        ]

    def __str__(self):
        """String representation of user."""
        if self.username:
            return self.username
        return f"{self.country_code}{self.phone_number}" if self.country_code else str(self.phone_number)

    def has_perm(self, perm, obj=None):
        """Check if user has specific permission."""
        return self.is_superuser

    def has_module_perms(self, app_label):
        """Check if user has permissions for app."""
        return self.is_superuser


class OTP(models.Model):
    """OTP model for phone number verification."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='otps'
    )
    phone_number = models.CharField(max_length=15)
    otp_code = models.CharField(max_length=10)
    is_verified = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta options for OTP model."""

        db_table = 'otps'
        verbose_name = 'OTP'
        verbose_name_plural = 'OTPs'
        indexes = [
            models.Index(fields=['phone_number', 'otp_code']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        """String representation of OTP."""
        return f"OTP for {self.phone_number}"

    def is_expired(self):
        """
        Check if OTP has expired.

        Returns:
            bool: True if OTP is expired
        """
        return timezone.now() > self.expires_at

    def verify(self):
        """
        Mark OTP as verified.

        Returns:
            bool: True if verification successful
        """
        if self.is_expired():
            return False
        self.is_verified = True
        self.save()
        return True

