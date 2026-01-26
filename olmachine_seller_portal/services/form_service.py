"""
Service for form validation and processing.
"""

import logging
import re
from django.core.exceptions import ValidationError
from olmachine_seller_portal.models import CategoryFormConfig, FormField

logger = logging.getLogger(__name__)


class FormService:
    """Service for form validation and data processing."""

    @staticmethod
    def get_form_config(category_code):
        """
        Get form configuration for a category.

        Args:
            category_code: Category code

        Returns:
            CategoryFormConfig: Form configuration

        Raises:
            CategoryFormConfig.DoesNotExist: If config not found
        """
        try:
            from olmachine_products.models import Category
            category = Category.objects.get(
                category_code=category_code,
                is_active=True
            )
            return category.form_config
        except Category.DoesNotExist:
            raise ValidationError(f"Category {category_code} not found")

    @staticmethod
    def validate_form_data(form_config, form_data):
        """
        Validate form data against form configuration.

        Args:
            form_config: CategoryFormConfig instance
            form_data: Dictionary of form field values

        Returns:
            dict: Validated and cleaned form data

        Raises:
            ValidationError: If validation fails
        """
        errors = {}
        validated_data = {}

        # Get all fields for this form config
        fields = form_config.fields.all().order_by('order')

        for field in fields:
            field_name = field.field_name
            field_value = form_data.get(field_name)

            # Check required fields
            if field.is_required and (
                field_value is None or
                field_value == '' or
                (isinstance(field_value, list) and len(field_value) == 0)
            ):
                errors[field_name] = (
                    f"{field.field_label} is required"
                )
                continue

            # Skip validation if field is empty and not required
            if not field.is_required and (
                field_value is None or
                field_value == '' or
                (isinstance(field_value, list) and len(field_value) == 0)
            ):
                validated_data[field_name] = (
                    field.default_value if field.default_value else None
                )
                continue

            # Type-specific validation
            try:
                validated_value = FormService._validate_field_type(
                    field,
                    field_value
                )
                validated_data[field_name] = validated_value
            except ValidationError as e:
                errors[field_name] = str(e)

        if errors:
            raise ValidationError(errors)

        return validated_data

    @staticmethod
    def _validate_field_type(field, value):
        """
        Validate field value based on field type.

        Args:
            field: FormField instance
            value: Field value to validate

        Returns:
            Validated value

        Raises:
            ValidationError: If validation fails
        """
        validation_rules = field.validation_rules or {}

        if field.field_type == 'number':
            try:
                if '.' in str(value):
                    value = float(value)
                else:
                    value = int(value)

                # Check min/max if specified
                if 'min' in validation_rules:
                    if value < validation_rules['min']:
                        raise ValidationError(
                            f"Value must be at least "
                            f"{validation_rules['min']}"
                        )
                if 'max' in validation_rules:
                    if value > validation_rules['max']:
                        raise ValidationError(
                            f"Value must be at most "
                            f"{validation_rules['max']}"
                        )
            except (ValueError, TypeError):
                raise ValidationError(
                    f"{field.field_label} must be a number"
                )

        elif field.field_type == 'email':
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, str(value)):
                raise ValidationError(
                    f"{field.field_label} must be a valid email"
                )

        elif field.field_type == 'url':
            url_regex = (
                r'^https?://(?:[-\w.])+(?:[:\d]+)?'
                r'(?:/(?:[\w/_.])*)?(?:\?(?:[\w&=%.])*)?'
                r'(?:#(?:[\w.])*)?$'
            )
            if not re.match(url_regex, str(value)):
                raise ValidationError(
                    f"{field.field_label} must be a valid URL"
                )

        elif field.field_type in ['select', 'radio']:
            # Validate against options
            if field.options:
                valid_values = [
                    opt.get('value') for opt in field.options
                ]
                if value not in valid_values:
                    raise ValidationError(
                        f"{field.field_label} must be one of: "
                        f"{', '.join(valid_values)}"
                    )

        elif field.field_type == 'checkbox':
            # Convert to boolean
            if isinstance(value, str):
                value = value.lower() in ['true', '1', 'yes', 'on']
            else:
                value = bool(value)

        # Check length constraints
        if isinstance(value, str):
            if 'min_length' in validation_rules:
                if len(value) < validation_rules['min_length']:
                    raise ValidationError(
                        f"{field.field_label} must be at least "
                        f"{validation_rules['min_length']} characters"
                    )
            if 'max_length' in validation_rules:
                if len(value) > validation_rules['max_length']:
                    raise ValidationError(
                        f"{field.field_label} must be at most "
                        f"{validation_rules['max_length']} characters"
                    )

            # Check regex pattern if specified
            if 'regex' in validation_rules:
                pattern = validation_rules['regex']
                if not re.match(pattern, value):
                    raise ValidationError(
                        f"{field.field_label} format is invalid"
                    )

        return value

