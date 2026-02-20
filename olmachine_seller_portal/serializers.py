"""
Serializers for olmachine_seller_portal app.
"""

from rest_framework import serializers
from olmachine_seller_portal.models import (
    CategoryFormConfig,
    SellerProfile,
    SellerProduct,
    ProductApproval
)
from olmachine_products.models import Category
from olmachine_products.serializers import ProductDetailsSerializer


class CategoryFormConfigSerializer(serializers.ModelSerializer):
    """Read-only serializer for form config (schema for frontend)."""

    category_code = serializers.CharField(source='category.category_code', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = CategoryFormConfig
        fields = ['id', 'category', 'category_code', 'category_name', 'is_active', 'schema']


class CategoryFormConfigCreateSerializer(serializers.ModelSerializer):
    """Create/update form config (admin)."""

    class Meta:
        model = CategoryFormConfig
        fields = ['category', 'is_active', 'schema']


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
    extra_info = serializers.JSONField()

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
            'extra_info',
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
    name = serializers.CharField(required=True)
    description = serializers.CharField(required=False, allow_blank=True)
    price = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        allow_null=True
    )
    currency = serializers.CharField(max_length=10, default='INR', required=False)
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
    extra_info = serializers.JSONField(required=False, default=dict)
    location = serializers.DictField(
        child=serializers.CharField(),
        required=False
    )

    def validate_category_code(self, value):
        """Validate category code exists and is leaf."""
        try:
            category = Category.objects.get(
                category_code=value,
                is_active=True
            )
            if not category.is_leaf_category():
                raise serializers.ValidationError(
                    "Products can only be listed under a leaf category. "
                    "Please select the final sub-category."
                )
            return value
        except Category.DoesNotExist:
            raise serializers.ValidationError(
                f"Category {value} does not exist"
            )

    def validate_extra_info(self, value):
        """Validate extra_info is a dictionary."""
        if value is not None and not isinstance(value, dict):
            raise serializers.ValidationError(
                "extra_info must be a dictionary"
            )
        return value or {}

    def validate(self, attrs):
        """If category has form config, ensure required schema fields are in extra_info."""
        from olmachine_seller_portal.models import CategoryFormConfig
        category_code = attrs.get('category_code')
        extra_info = attrs.get('extra_info') or {}
        try:
            config = CategoryFormConfig.objects.get(
                category__category_code=category_code,
                is_active=True
            )
        except CategoryFormConfig.DoesNotExist:
            return attrs
        schema = config.schema or []
        for field in schema:
            if field.get('is_required') and not field.get('field_name'):
                continue
            name = field.get('field_name')
            if not name:
                continue
            if field.get('is_required'):
                val = extra_info.get(name)
                if val is None or val == '' or (isinstance(val, list) and len(val) == 0):
                    label = field.get('field_label') or name
                    raise serializers.ValidationError({
                        'extra_info': f"'{label}' is required."
                    }
                    )
        return attrs


class SellerProductUpdateSerializer(serializers.Serializer):
    """Serializer for updating seller product."""

    category_code = serializers.CharField(required=False)
    name = serializers.CharField(required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    price = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        allow_null=True
    )
    currency = serializers.CharField(max_length=10, required=False)
    tag = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        allow_null=True
    )
    availability = serializers.CharField(max_length=50, required=False)
    extra_info = serializers.JSONField(required=False)
    location = serializers.DictField(
        child=serializers.CharField(),
        required=False
    )

    def validate_category_code(self, value):
        """Validate category code exists and is leaf."""
        try:
            category = Category.objects.get(
                category_code=value,
                is_active=True
            )
            if not category.is_leaf_category():
                raise serializers.ValidationError(
                    "Products can only be listed under a leaf category. "
                    "Please select the final sub-category."
                )
            return value
        except Category.DoesNotExist:
            raise serializers.ValidationError(
                f"Category {value} does not exist"
            )

    def validate_extra_info(self, value):
        """Validate extra_info is a dictionary."""
        if value is not None and not isinstance(value, dict):
            raise serializers.ValidationError(
                "extra_info must be a dictionary"
            )
        return value

    def validate(self, attrs):
        """
        Validate required schema fields with effective update payload.
        """
        from olmachine_seller_portal.models import CategoryFormConfig

        instance = self.instance
        if not instance:
            return attrs

        category_code = attrs.get(
            'category_code',
            instance.product.category.category_code
        )

        effective_extra_info = dict(instance.extra_info or {})
        if 'extra_info' in attrs:
            effective_extra_info = attrs.get('extra_info') or {}

        try:
            config = CategoryFormConfig.objects.get(
                category__category_code=category_code,
                is_active=True
            )
        except CategoryFormConfig.DoesNotExist:
            return attrs

        schema = config.schema or []
        for field in schema:
            if field.get('is_required') and not field.get('field_name'):
                continue
            name = field.get('field_name')
            if not name:
                continue
            if field.get('is_required'):
                value = effective_extra_info.get(name)
                if (
                    value is None
                    or value == ''
                    or (isinstance(value, list) and len(value) == 0)
                ):
                    label = field.get('field_label') or name
                    raise serializers.ValidationError({
                        'extra_info': f"'{label}' is required."
                    })

        return attrs


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

