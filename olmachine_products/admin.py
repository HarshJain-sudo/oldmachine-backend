"""Admin configuration for olmachine_products app."""

from django.contrib import admin
from .models import (
    Category,
    Seller,
    Location,
    Product,
    ProductImage,
    ProductSpecification,
    UserCategoryView
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin interface for Category model."""

    list_display = (
        'name',
        'category_code',
        'parent_category',
        'level',
        'order',
        'is_active',
        'is_leaf_category_display',
        'created_at'
    )
    list_filter = ('is_active', 'level', 'parent_category', 'created_at')
    search_fields = ('name', 'category_code')
    ordering = ('level', 'order', 'name')
    raw_id_fields = ('parent_category',)

    def is_leaf_category_display(self, obj):
        """Display if category is a leaf category."""
        return obj.is_leaf_category()
    is_leaf_category_display.boolean = True
    is_leaf_category_display.short_description = 'Is Leaf'

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('parent_category')


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    """Admin interface for Seller model."""

    list_display = ('name', 'created_at')
    search_fields = ('name',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """Admin interface for Location model."""

    list_display = ('state', 'district', 'created_at')
    list_filter = ('state',)
    search_fields = ('state', 'district')


class ProductImageInline(admin.TabularInline):
    """Inline admin for ProductImage."""

    model = ProductImage
    extra = 1


class ProductSpecificationInline(admin.TabularInline):
    """Inline admin for ProductSpecification."""

    model = ProductSpecification
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin interface for Product model."""

    list_display = (
        'name',
        'product_code',
        'category',
        'seller',
        'price',
        'currency',
        'availability',
        'is_active',
        'created_at'
    )
    list_filter = (
        'category',
        'availability',
        'is_active',
        'created_at'
    )
    search_fields = ('name', 'product_code', 'description')
    inlines = [ProductImageInline, ProductSpecificationInline]
    ordering = ('-created_at',)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """Admin interface for ProductImage model."""

    list_display = ('product', 'image_url', 'order', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('product__name',)


@admin.register(ProductSpecification)
class ProductSpecificationAdmin(admin.ModelAdmin):
    """Admin interface for ProductSpecification model."""

    list_display = ('product', 'key', 'value', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('product__name', 'key', 'value')


@admin.register(UserCategoryView)
class UserCategoryViewAdmin(admin.ModelAdmin):
    """Admin interface for UserCategoryView model."""

    list_display = ('user', 'category', 'viewed_at', 'updated_at')
    list_filter = ('viewed_at', 'category')
    search_fields = (
        'user__phone_number',
        'user__username',
        'category__name',
        'category__category_code'
    )
    readonly_fields = ('viewed_at', 'updated_at')
    ordering = ('-viewed_at',)

