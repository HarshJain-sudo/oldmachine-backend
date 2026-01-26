"""
Serializers for olmachine_seller_portal app.
"""

from rest_framework import serializers
from olmachine_seller_portal.models import (
    CategoryFormConfig,
    FormField,
    SellerProfile,
    SellerProduct,
    ProductApproval
)
from olmachine_products.models import Category, Product, Location
from olmachine_products.serializers import (
    CategoryDetailSerializer,
    ProductDetailsSerializer
)


class FormFieldSerializer(serializers.ModelSerializer):
    """Serializer for form field configuration."""

    class Meta:
        """Meta options for FormFieldSerializer."""

        model = FormField
        fields = [
            'id',
            'field_name',
            'field_label',
            'field_type',
            'is_required',
            'placeholder',
            'help_text',
            'default_value',
            'validation_rules',
            'options',
            'order'
        ]


class CategoryFormConfigSerializer(serializers.ModelSerializer):
    """Serializer for category form configuration."""

    fields = FormFieldSerializer(many=True, read_only=True)
    category_name = serializers.CharField(
        source='category.name',
        read_only=True
    )
    category_code = serializers.CharField(
        source='category.category_code',
        read_only=True
    )

    class Meta:
        """Meta options for CategoryFormConfigSerializer."""

        model = CategoryFormConfig
        fields = [
            'id',
            'category',
            'category_name',
            'category_code',
            'is_active',
            'fields',
            'created_at',
            'updated_at'
        ]


class CategoryFormConfigCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating category form configuration with fields."""

    fields = FormFieldSerializer(many=True)

    class Meta:
        """Meta options for CategoryFormConfigCreateSerializer."""

        model = CategoryFormConfig
        fields = ['category', 'is_active', 'fields']

    def create(self, validated_data):
        """Create form config with fields."""
        fields_data = validated_data.pop('fields')
        form_config = CategoryFormConfig.objects.create(**validated_data)

        for field_data in fields_data:
            FormField.objects.create(
                form_config=form_config,
                **field_data
            )

        return form_config

    def update(self, instance, validated_data):
        """Update form config with fields."""
        fields_data = validated_data.pop('fields', None)

        instance.is_active = validated_data.get(
            'is_active',
            instance.is_active
        )
        instance.save()

        if fields_data is not None:
            # Delete existing fields
            instance.fields.all().delete()

            # Create new fields
            for field_data in fields_data:
                FormField.objects.create(
                    form_config=instance,
                    **field_data
                )

        return instance


class SellerProfileSerializer(serializers.ModelSerializer):
    """Serializer for seller profile."""

    seller_name = serializers.CharField(
        source='seller.name',
        read_only=True
    )
    user_phone = serializers.SerializerMethodField()

    class Meta:
        """Meta options for SellerProfileSerializer."""

        model = SellerProfile
        fields = [
            'id',
            'seller',
            'seller_name',
            'user',
            'user_phone',
            'business_name',
            'business_address',
            'phone_number',
            'email',
            'is_verified',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_user_phone(self, obj):
        """Get user phone number."""
        if obj.user.phone_number:
            return (
                f"{obj.user.country_code}{obj.user.phone_number}"
                if obj.user.country_code
                else obj.user.phone_number
            )
        return None


class ProductFormDataSerializer(serializers.Serializer):
    """Serializer for product form data from seller."""

    # Common fields that might be in form
    name = serializers.CharField(required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    price = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        allow_null=True
    )
    currency = serializers.CharField(
        max_length=10,
        default='INR',
        required=False
    )
    tag = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        allow_null=True
    )
    availability = serializers.CharField(
        max_length=50,
        default='In Stock',
        required=False
    )

    # Dynamic fields will be stored as JSON
    def to_representation(self, instance):
        """Return form data as dictionary."""
        if isinstance(instance, dict):
            return instance
        return super().to_representation(instance)


class SellerProductSerializer(serializers.ModelSerializer):
    """Serializer for seller product."""

    product_details = ProductDetailsSerializer(
        source='product',
        read_only=True
    )
    seller_name = serializers.CharField(
        source='seller.name',
        read_only=True
    )
    approved_by_name = serializers.CharField(
        source='approved_by.username',
        read_only=True
    )
    form_data = serializers.JSONField()

    class Meta:
        """Meta options for SellerProductSerializer."""

        model = SellerProduct
        fields = [
            'id',
            'product',
            'product_details',
            'seller',
            'seller_name',
            'status',
            'rejection_reason',
            'approved_by',
            'approved_by_name',
            'approved_at',
            'form_data',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'approved_by',
            'approved_at'
        ]


class SellerProductCreateSerializer(serializers.Serializer):
    """Serializer for creating seller product."""

    category_code = serializers.CharField(required=True)
    form_data = serializers.JSONField(required=True)
    location = serializers.DictField(
        child=serializers.CharField(),
        required=False
    )

    def validate_category_code(self, value):
        """Validate category code."""
        try:
            category = Category.objects.get(
                category_code=value,
                is_active=True
            )
            # Check if form config exists
            if not hasattr(category, 'form_config'):
                raise serializers.ValidationError(
                    f"No form configuration found for category {value}"
                )
            if not category.form_config.is_active:
                raise serializers.ValidationError(
                    f"Form is not active for category {value}"
                )
            return value
        except Category.DoesNotExist:
            raise serializers.ValidationError(
                f"Category {value} does not exist"
            )

    def validate_form_data(self, value):
        """Validate form data."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Form data must be a dictionary"
            )
        return value


class ProductApprovalSerializer(serializers.ModelSerializer):
    """Serializer for product approval."""

    reviewed_by_name = serializers.CharField(
        source='reviewed_by.username',
        read_only=True
    )
    product_name = serializers.CharField(
        source='seller_product.product.name',
        read_only=True
    )

    class Meta:
        """Meta options for ProductApprovalSerializer."""

        model = ProductApproval
        fields = [
            'id',
            'seller_product',
            'product_name',
            'status',
            'reviewed_by',
            'reviewed_by_name',
            'comments',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at'
        ]

