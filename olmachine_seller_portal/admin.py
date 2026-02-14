"""Admin configuration for olmachine_seller_portal app."""

from django.contrib import admin
from .models import (
    CategoryFormConfig,
    SellerProfile,
    SellerProduct,
    ProductApproval
)


@admin.register(CategoryFormConfig)
class CategoryFormConfigAdmin(admin.ModelAdmin):
    """Form config per category. schema = JSON array of field defs for frontend."""

    list_display = ('category', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('category__name', 'category__category_code')
    ordering = ('-created_at',)


@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    """Admin interface for SellerProfile model."""

    list_display = (
        'seller',
        'user',
        'business_name',
        'is_verified',
        'created_at'
    )
    list_filter = ('is_verified', 'created_at')
    search_fields = (
        'seller__name',
        'business_name',
        'user__phone_number',
        'user__username'
    )
    ordering = ('-created_at',)


@admin.register(SellerProduct)
class SellerProductAdmin(admin.ModelAdmin):
    """Admin interface for SellerProduct model."""

    list_display = (
        'product',
        'seller',
        'status',
        'approved_by',
        'created_at'
    )
    list_filter = ('status', 'created_at')
    search_fields = (
        'product__name',
        'product__product_code',
        'seller__name'
    )
    readonly_fields = ('approved_at',)
    ordering = ('-created_at',)


@admin.register(ProductApproval)
class ProductApprovalAdmin(admin.ModelAdmin):
    """Admin interface for ProductApproval model."""

    list_display = (
        'seller_product',
        'status',
        'reviewed_by',
        'created_at'
    )
    list_filter = ('status', 'created_at')
    search_fields = (
        'seller_product__product__name',
        'reviewed_by__username'
    )
    ordering = ('-created_at',)
