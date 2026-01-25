"""
Serializers for olmachine_users app.
"""

from rest_framework import serializers
from olmachine_users.models import User
from olmachine_users.utils.validators import (
    validate_phone_number,
    validate_country_code,
    validate_otp
)


class LoginOrSignUpSerializer(serializers.Serializer):
    """Serializer for login or sign up request."""

    phone_number = serializers.CharField(max_length=15)
    country_code = serializers.CharField(max_length=5)

    def validate_phone_number(self, value):
        """
        Validate phone number.

        Args:
            value: Phone number value

        Returns:
            str: Validated phone number
        """
        try:
            validate_phone_number(value)
        except Exception as e:
            raise serializers.ValidationError(str(e))
        return value

    def validate_country_code(self, value):
        """
        Validate country code.

        Args:
            value: Country code value

        Returns:
            str: Validated country code
        """
        try:
            validate_country_code(value)
        except Exception as e:
            raise serializers.ValidationError(str(e))
        return value


class VerifyOTPSerializer(serializers.Serializer):
    """Serializer for OTP verification request."""

    phone_number = serializers.CharField(max_length=15)
    otp = serializers.CharField(max_length=10)

    def validate_phone_number(self, value):
        """
        Validate phone number.

        Args:
            value: Phone number value

        Returns:
            str: Validated phone number
        """
        try:
            validate_phone_number(value)
        except Exception as e:
            raise serializers.ValidationError(str(e))
        return value

    def validate_otp(self, value):
        """
        Validate OTP.

        Args:
            value: OTP value

        Returns:
            str: Validated OTP
        """
        try:
            validate_otp(value)
        except Exception as e:
            raise serializers.ValidationError(str(e))
        return value

