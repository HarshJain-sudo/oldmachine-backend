"""Admin configuration for olmachine_users app."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, OTP


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for User model."""

    list_display = (
        'id',
        'username',
        'phone_number',
        'country_code',
        'is_active',
        'is_staff',
        'created_at'
    )
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'created_at')
    search_fields = ('username', 'phone_number', 'id')
    ordering = ('-created_at',)
    filter_horizontal = ()
    readonly_fields = ('id', 'created_at', 'updated_at')

    fieldsets = (
        (
            None,
            {
                'fields': (
                    'id',
                    'username',
                    'phone_number',
                    'country_code',
                    'password'
                )
            }
        ),
        (
            'Permissions',
            {'fields': ('is_active', 'is_staff', 'is_superuser')}
        ),
        ('Important dates', {'fields': ('created_at', 'updated_at')}),
    )

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'username',
                    'password1',
                    'password2',
                ),
            },
        ),
    )


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    """Admin interface for OTP model."""

    list_display = (
        'phone_number',
        'otp_code',
        'is_verified',
        'expires_at',
        'created_at'
    )
    list_filter = ('is_verified', 'expires_at', 'created_at')
    search_fields = ('phone_number', 'otp_code')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

