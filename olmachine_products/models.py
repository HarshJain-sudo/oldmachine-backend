"""
Product models for olmachine_products app.
"""

import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings


class Category(models.Model):
    """Category model for product categorization with hierarchical support."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    category_code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    parent_category = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='sub_categories',
        null=True,
        blank=True,
        help_text="Parent category (null for top-level categories)"
    )
    level = models.IntegerField(
        default=0,
        help_text="Depth level in hierarchy (0 = top level)"
    )
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
        ordering = ['level', 'order', 'name']
        indexes = [
            models.Index(fields=['category_code']),
            models.Index(fields=['parent_category', 'is_active', 'order']),
            models.Index(fields=['level', 'is_active']),
            models.Index(fields=['is_active', 'order']),
        ]

    def __str__(self):
        """String representation of category."""
        return f"{self.name} ({self.category_code})"

    def save(self, *args, **kwargs):
        """Override save to auto-calculate level."""
        if self.parent_category:
            self.level = self.parent_category.level + 1
        else:
            self.level = 0
        super().save(*args, **kwargs)

    def get_ancestors(self):
        """
        Get all parent categories up to root.

        Returns:
            QuerySet: All ancestor categories ordered from root to parent
        """
        ancestors = []
        current = self.parent_category
        while current:
            ancestors.insert(0, current)
            current = current.parent_category
        return ancestors

    def get_descendants(self):
        """
        Get all child categories recursively.

        Returns:
            QuerySet: All descendant categories
        """
        descendants = list(self.sub_categories.all())
        for child in self.sub_categories.all():
            descendants.extend(child.get_descendants())
        return descendants

    def get_all_descendant_ids(self):
        """
        Get all descendant category IDs including self.

        Returns:
            list: List of category IDs
        """
        ids = [self.id]
        for child in self.sub_categories.filter(is_active=True):
            ids.extend(child.get_all_descendant_ids())
        return ids

    def is_leaf_category(self):
        """
        Check if category has no children.

        Returns:
            bool: True if category has no active sub-categories
        """
        return not self.sub_categories.filter(is_active=True).exists()

    def get_full_path(self):
        """
        Get full category path as string.

        Returns:
            str: Full path like "Electronics > Mobile Phones > Smartphones"
        """
        path = [self.name]
        current = self.parent_category
        while current:
            path.insert(0, current.name)
            current = current.parent_category
        return ' > '.join(path)


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
            models.Index(fields=['price']),
            models.Index(fields=['location']),
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
    """
    Product specification model for storing product specs (key-value).

    Buyer filters use canonical keys: 'condition' and 'year'. Seller portal
    CategoryFormConfig should use these keys so marketplace filters work.
    See olmachine_products.constants (PRODUCT_SPEC_CONDITION_KEY,
    PRODUCT_SPEC_YEAR_KEY).
    """

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
            models.Index(fields=['product', 'key']),
            models.Index(fields=['product', 'key', 'value']),
        ]

    def __str__(self):
        """String representation of product specification."""
        return f"{self.product.name} - {self.key}: {self.value}"


class UserCategoryView(models.Model):
    """
    Model to track user's recently viewed categories.
    Stores last 3 categories viewed by each user.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='category_views'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='user_views'
    )
    viewed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta options for UserCategoryView."""

        db_table = 'user_category_views'
        verbose_name = 'User Category View'
        verbose_name_plural = 'User Category Views'
        ordering = ['-viewed_at']
        indexes = [
            models.Index(fields=['user', '-viewed_at']),
            models.Index(fields=['category']),
        ]
        unique_together = [['user', 'category']]

    def __str__(self):
        """String representation of user category view."""
        return f"{self.user.phone_number} viewed {self.category.name}"


class SavedSearch(models.Model):
    """
    Saved search for authenticated buyers. Stores filter/sort/pagination
    so the frontend can restore the search (e.g. same body as product
    listings search API).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_searches'
    )
    name = models.CharField(max_length=255, blank=True, null=True)
    category_code = models.CharField(max_length=50, blank=True, null=True)
    query_params = models.JSONField(
        default=dict,
        help_text='Filter/sort/search params (e.g. same as search API body)'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta options for SavedSearch."""

        db_table = 'saved_searches'
        verbose_name = 'Saved Search'
        verbose_name_plural = 'Saved Searches'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        """String representation of saved search."""
        label = self.name or self.category_code or 'Saved search'
        return f"SavedSearch {self.id} - {label}"

