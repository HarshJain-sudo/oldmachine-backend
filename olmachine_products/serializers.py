"""
Serializers for olmachine_products app.
"""

from rest_framework import serializers
from olmachine_products.models import (
    Category,
    Product,
    ProductImage,
    ProductSpecification,
    Seller,
    Location,
    SavedSearch,
)
from olmachine_products.services.recommendation_service import (
    RecommendationService
)


class ProductDetailSerializer(serializers.ModelSerializer):
    """Serializer for product detail in category listing."""

    image_url = serializers.SerializerMethodField()
    extra_config = serializers.SerializerMethodField()

    class Meta:
        """Meta options for ProductDetailSerializer."""

        model = Product
        fields = ['name', 'product_code', 'extra_config', 'image_url']

    def get_image_url(self, obj):
        """Get first product image URL."""
        first_image = obj.images.first()
        return first_image.image_url if first_image else None

    def get_extra_config(self, obj):
        """Get extra configuration from specifications."""
        specs = obj.specifications.all()
        if specs:
            return ', '.join([f"{s.key}: {s.value}" for s in specs[:2]])
        return None


class CategoryDetailSerializer(serializers.ModelSerializer):
    """Serializer for category details with hierarchy info."""

    parent_category = serializers.CharField(
        source='parent_category.category_code',
        read_only=True,
        allow_null=True
    )
    parent_category_name = serializers.CharField(
        source='parent_category.name',
        read_only=True,
        allow_null=True
    )
    id = serializers.UUIDField(read_only=True)

    class Meta:
        """Meta options for CategoryDetailSerializer."""

        model = Category
        fields = [
            'id',
            'name',
            'category_code',
            'description',
            'level',
            'parent_category',
            'parent_category_name',
            'order',
            'image_url'
        ]


class SellerDetailSerializer(serializers.ModelSerializer):
    """Serializer for seller details."""

    class Meta:
        """Meta options for SellerDetailSerializer."""

        model = Seller
        fields = ['name']


class LocationDetailSerializer(serializers.ModelSerializer):
    """Serializer for location details."""

    class Meta:
        """Meta options for LocationDetailSerializer."""

        model = Location
        fields = ['state', 'district']


class ProductSpecificationSerializer(serializers.ModelSerializer):
    """Serializer for product specifications as dictionary."""

    class Meta:
        """Meta options for ProductSpecificationSerializer."""

        model = ProductSpecification
        fields = ['key', 'value']

    def to_representation(self, instance):
        """Convert to dictionary format."""
        return {instance.key: instance.value}


class CategoryProductDetailSerializer(serializers.ModelSerializer):
    """Serializer for product details in category products listing."""

    seller_details = SellerDetailSerializer(source='seller', read_only=True)
    image_urls = serializers.SerializerMethodField()
    location_details = LocationDetailSerializer(
        source='location',
        read_only=True
    )
    product_specifications = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        """Meta options for CategoryProductDetailSerializer."""

        model = Product
        fields = [
            'name',
            'product_code',
            'seller_details',
            'tag',
            'image_urls',
            'location_details',
            'product_specifications',
            'price',
            'currency'
        ]

    def get_image_urls(self, obj):
        """Get all product image URLs."""
        return [
            img.image_url
            for img in obj.images.order_by('order')
        ]

    def get_product_specifications(self, obj):
        """Get product specifications as dictionary."""
        specs = obj.specifications.all()
        return {
            spec.key: spec.value
            for spec in specs
        }

    def get_price(self, obj):
        """Get price as string for consistency with ProductDetailsSerializer."""
        return str(obj.price) if obj.price else None


class ProductDetailsSerializer(serializers.ModelSerializer):
    """Serializer for detailed product information."""

    seller_details = SellerDetailSerializer(source='seller', read_only=True)
    image_urls = serializers.SerializerMethodField()
    location_details = LocationDetailSerializer(
        source='location',
        read_only=True
    )
    product_specifications = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        """Meta options for ProductDetailsSerializer."""

        model = Product
        fields = [
            'name',
            'product_code',
            'description',
            'seller_details',
            'tag',
            'image_urls',
            'location_details',
            'product_specifications',
            'price',
            'currency',
            'availability'
        ]

    def get_image_urls(self, obj):
        """Get all product image URLs."""
        return [
            img.image_url
            for img in obj.images.order_by('order')
        ]

    def get_product_specifications(self, obj):
        """Get product specifications as dictionary."""
        specs = obj.specifications.all()
        return {
            spec.key: spec.value
            for spec in specs
        }

    def get_price(self, obj):
        """Get price as string."""
        return str(obj.price) if obj.price else None


class RecommendedCategorySerializer(serializers.Serializer):
    """Serializer for recommended category with products."""

    category_name = serializers.CharField()
    category_code = serializers.CharField()
    category_image_url = serializers.URLField(allow_null=True)
    products = ProductDetailSerializer(many=True)


class SavedSearchSerializer(serializers.ModelSerializer):
    """Read serializer for SavedSearch."""

    class Meta:
        """Meta options for SavedSearchSerializer."""

        model = SavedSearch
        fields = ['id', 'name', 'category_code', 'query_params', 'created_at']
        read_only_fields = ['id', 'created_at']


class SavedSearchCreateSerializer(serializers.Serializer):
    """Serializer for creating SavedSearch (POST body)."""

    name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    category_code = serializers.CharField(
        max_length=50, required=False, allow_blank=True
    )
    query_params = serializers.JSONField(default=dict)

    def validate_query_params(self, value):
        """Ensure query_params is a dictionary."""
        if value is not None and not isinstance(value, dict):
            raise serializers.ValidationError("query_params must be a dictionary")
        return value or {}

