"""
Models for olmachine_seller_portal app.
"""

import uuid
import json
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from olmachine_products.models import Category, Seller, Product, ProductImage


class CategoryFormConfig(models.Model):
    """
    Form configuration for each category.
    Each category can have one form configuration.
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta options for CategoryFormConfig."""

        db_table = 'category_form_configs'
        verbose_name = 'Category Form Configuration'
        verbose_name_plural = 'Category Form Configurations'
        indexes = [
            models.Index(fields=['category', 'is_active']),
        ]

    def __str__(self):
        """String representation of category form config."""
        return f"Form Config for {self.category.name}"


class FormField(models.Model):
    """
    Individual field configuration within a form.
    """

    FIELD_TYPE_CHOICES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('textarea', 'Textarea'),
        ('select', 'Select'),
        ('radio', 'Radio'),
        ('checkbox', 'Checkbox'),
        ('file', 'File'),
        ('date', 'Date'),
        ('email', 'Email'),
        ('url', 'URL'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    form_config = models.ForeignKey(
        CategoryFormConfig,
        on_delete=models.CASCADE,
        related_name='fields'
    )
    field_name = models.CharField(
        max_length=100,
        help_text="Internal field name (e.g., 'brand', 'model')"
    )
    field_label = models.CharField(
        max_length=255,
        help_text="Display label (e.g., 'Brand Name')"
    )
    field_type = models.CharField(
        max_length=20,
        choices=FIELD_TYPE_CHOICES,
        default='text'
    )
    is_required = models.BooleanField(default=False)
    placeholder = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    help_text = models.TextField(blank=True, null=True)
    default_value = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    validation_rules = models.JSONField(
        default=dict,
        blank=True,
        help_text=(
            "Validation rules: "
            "{'min_length': 5, 'max_length': 100, 'regex': 'pattern'}"
        )
    )
    options = models.JSONField(
        default=list,
        blank=True,
        help_text=(
            "For select/radio: "
            "[{'value': 'option1', 'label': 'Option 1'}]"
        )
    )
    order = models.IntegerField(
        default=0,
        help_text="Display order of field"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta options for FormField."""

        db_table = 'form_fields'
        verbose_name = 'Form Field'
        verbose_name_plural = 'Form Fields'
        ordering = ['order', 'field_label']
        indexes = [
            models.Index(fields=['form_config', 'order']),
        ]
        unique_together = [['form_config', 'field_name']]

    def __str__(self):
        """String representation of form field."""
        return f"{self.field_label} ({self.field_type})"


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
    form_data = models.JSONField(
        default=dict,
        help_text="Store all form field values as JSON"
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
