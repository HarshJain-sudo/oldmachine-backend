"""
Product models for olmachine_products app.
"""

import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    """Category model for product categorization."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    category_code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    order = models.IntegerField(
        default=0,
        help_text="Display order of category"
    )
    image_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta options for Category model."""

        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['category_code']),
            models.Index(fields=['is_active', 'order']),
        ]

    def __str__(self):
        """String representation of category."""
        return f"{self.name} ({self.category_code})"


class Seller(models.Model):
    """Seller model for product sellers."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta options for Seller model."""

        db_table = 'sellers'
        verbose_name = 'Seller'
        verbose_name_plural = 'Sellers'

    def __str__(self):
        """String representation of seller."""
        return self.name


class Location(models.Model):
    """Location model for product location details."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta options for Location model."""

        db_table = 'locations'
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'
        unique_together = [['state', 'district']]

    def __str__(self):
        """String representation of location."""
        if self.district:
            return f"{self.district}, {self.state}"
        return self.state


class Product(models.Model):
    """Product model for marketplace products."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    product_code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products'
    )
    seller = models.ForeignKey(
        Seller,
        on_delete=models.CASCADE,
        related_name='products'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        related_name='products',
        null=True,
        blank=True
    )
    tag = models.CharField(max_length=100, blank=True, null=True)
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    currency = models.CharField(max_length=10, default='INR')
    availability = models.CharField(
        max_length=50,
        default='In Stock',
        choices=[
            ('In Stock', 'In Stock'),
            ('Out of Stock', 'Out of Stock'),
            ('Limited Stock', 'Limited Stock'),
        ]
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta options for Product model."""

        db_table = 'products'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product_code']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['seller']),
        ]

    def __str__(self):
        """String representation of product."""
        return f"{self.name} ({self.product_code})"


class ProductImage(models.Model):
    """Product image model for storing product images."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image_url = models.URLField()
    order = models.IntegerField(
        default=0,
        help_text="Display order of image"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta options for ProductImage model."""

        db_table = 'product_images'
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'
        ordering = ['order', 'created_at']
        indexes = [
            models.Index(fields=['product', 'order']),
        ]

    def __str__(self):
        """String representation of product image."""
        return f"Image for {self.product.name}"


class ProductSpecification(models.Model):
    """Product specification model for storing product specs."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='specifications'
    )
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta options for ProductSpecification model."""

        db_table = 'product_specifications'
        verbose_name = 'Product Specification'
        verbose_name_plural = 'Product Specifications'
        unique_together = [['product', 'key']]
        indexes = [
            models.Index(fields=['product']),
        ]

    def __str__(self):
        """String representation of product specification."""
        return f"{self.product.name} - {self.key}: {self.value}"

