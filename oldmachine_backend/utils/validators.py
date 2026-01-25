"""
Validation utility functions.
"""

import re
from django.core.exceptions import ValidationError


def validate_phone_number(phone_number):
    """
    Validate phone number format.

    Args:
        phone_number: Phone number string

    Raises:
        ValidationError: If phone number is invalid
    """
    if not phone_number:
        raise ValidationError("Phone number is required")

    # Remove any spaces or special characters
    cleaned_phone = re.sub(r'[^\d]', '', phone_number)

    # Check if phone number is 10 digits
    if not re.match(r'^\d{10}$', cleaned_phone):
        raise ValidationError("Phone number must be 10 digits")


def validate_country_code(country_code):
    """
    Validate country code format.

    Args:
        country_code: Country code string (e.g., '+91')

    Raises:
        ValidationError: If country code is invalid
    """
    if not country_code:
        raise ValidationError("Country code is required")

    # Check if country code starts with + and has 1-4 digits
    if not re.match(r'^\+\d{1,4}$', country_code):
        raise ValidationError(
            "Country code must start with + followed by 1-4 digits"
        )


def validate_otp(otp):
    """
    Validate OTP format.

    Args:
        otp: OTP string

    Raises:
        ValidationError: If OTP is invalid
    """
    if not otp:
        raise ValidationError("OTP is required")

    # Check if OTP is numeric
    # For development, accept "000000" (6 digits) or configured length
    from django.conf import settings
    otp_length = getattr(settings, 'OTP_LENGTH', 6)

    # Allow "000000" for development or standard length
    if otp == "000000" or re.match(rf'^\d{{{otp_length}}}$', otp):
        return
    
    raise ValidationError(
        f"OTP must be {otp_length} digits or '000000' for development"
    )

