"""
Models for olmachine_seller_portal app.
"""

import uuid
from django.db import models
from django.conf import settings
from olmachine_products.models import Category, Seller, Product, ProductImage


# Max depth for category tree in seller portal (root = 0, so levels 0..4 = 5 levels)
MAX_CATEGORY_DEPTH = 5


class CategoryFormConfig(models.Model):
    """
    Form configuration for a category (leaf only).
    schema: JSON array of field definitions for frontend to render the form.
    Example: [{"field_name": "brand", "field_label": "Brand", "field_type": "text",
               "is_required": true, "order": 1, "options": []}]
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    category = models.OneToOneField(
        Category,
        on_delete=models.CASCADE,
        related_name='form_config'
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Enable/disable form for this category"
    )
    schema = models.JSONField(
        default=list,
        help_text=(
            "Form schema for frontend: array of "
            "{field_name, field_label, field_type, is_required, order, options, ...}"
        )
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'category_form_configs'
        verbose_name = 'Category Form Configuration'
        verbose_name_plural = 'Category Form Configurations'
        indexes = [
            models.Index(fields=['category', 'is_active']),
        ]

    def __str__(self):
        return f"Form Config for {self.category.name}"


class SellerProfile(models.Model):
    """
    Extended seller profile linking sellers to users.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    seller = models.OneToOneField(
        Seller,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='seller_profiles',
        help_text="Link seller to authenticated user"
    )
    business_name = models.CharField(max_length=255, blank=True, null=True)
    business_address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta options for SellerProfile."""

        db_table = 'seller_profiles'
        verbose_name = 'Seller Profile'
        verbose_name_plural = 'Seller Profiles'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['seller']),
        ]

    def __str__(self):
        """String representation of seller profile."""
        return f"Profile for {self.seller.name}"


class SellerProduct(models.Model):
    """
    Products created by sellers with approval status.
    Links to existing Product model.
    """

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('listed', 'Listed'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name='seller_product'
    )
    seller = models.ForeignKey(
        Seller,
        on_delete=models.CASCADE,
        related_name='seller_products'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    rejection_reason = models.TextField(blank=True, null=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='approved_products',
        null=True,
        blank=True
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    extra_info = models.JSONField(
        default=dict,
        blank=True,
        help_text="Extra product information as key-value JSON"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta options for SellerProduct."""

        db_table = 'seller_products'
        verbose_name = 'Seller Product'
        verbose_name_plural = 'Seller Products'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['seller', 'status']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        """String representation of seller product."""
        return f"{self.product.name} - {self.get_status_display()}"


class ProductApproval(models.Model):
    """
    Track approval history and comments for products.
    Future: Multi-level approval tracking.
    """

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    seller_product = models.ForeignKey(
        SellerProduct,
        on_delete=models.CASCADE,
        related_name='approvals'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='product_reviews',
        null=True,
        blank=True
    )
    comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta options for ProductApproval."""

        db_table = 'product_approvals'
        verbose_name = 'Product Approval'
        verbose_name_plural = 'Product Approvals'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['seller_product', 'status']),
        ]

    def __str__(self):
        """String representation of product approval."""
        return (
            f"{self.seller_product.product.name} - "
            f"{self.get_status_display()}"
        )
