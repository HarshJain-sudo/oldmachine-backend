"""
Validation utilities for olmachine_users app.
"""

from django.core.exceptions import ValidationError
from oldmachine_backend.utils.validators import (
    validate_phone_number as base_validate_phone_number,
    validate_country_code as base_validate_country_code,
    validate_otp as base_validate_otp
)

# Re-export validators
validate_phone_number = base_validate_phone_number
validate_country_code = base_validate_country_code
validate_otp = base_validate_otp

