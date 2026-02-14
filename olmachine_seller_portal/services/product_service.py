"""
Service for seller product creation and management.
"""

import logging
from django.db import transaction
from olmachine_products.models import (
    Category,
    Product,
    Location,
    ProductImage,
    ProductSpecification,
    Seller
)
from olmachine_seller_portal.models import SellerProduct

logger = logging.getLogger(__name__)


class ProductService:
    """Service for seller product management."""

    @staticmethod
    def create_seller_product(
        seller,
        category_code,
        name,
        description='',
        price=None,
        currency='INR',
        tag=None,
        availability='In Stock',
        extra_info=None,
        images=None,
        location_data=None
    ):
        """
        Create a product from seller submission.

        Args:
            seller: Seller instance
            category_code: Category code
            name: Product name (required)
            description: Product description
            price: Product price
            currency: Currency code
            tag: Product tag
            availability: Availability status
            extra_info: Extra product info as key-value dict
            images: List of image files (optional)
            location_data: Location data dict (optional)

        Returns:
            SellerProduct: Created seller product

        Raises:
            ValueError: If creation fails
        """
        extra_info = extra_info or {}
        try:
            with transaction.atomic():
                # Get category and verify it's a leaf category
                category = Category.objects.get(
                    category_code=category_code,
                    is_active=True
                )

                # Products can only be assigned to leaf categories
                if not category.is_leaf_category():
                    raise ValueError(
                        "Products can only be assigned to leaf categories "
                        "(categories with no sub-categories). "
                        f"Category '{category.name}' has sub-categories."
                    )

                # Generate unique product code
                product_code = ProductService._generate_product_code(
                    category_code
                )

                # Get or create location
                location = None
                if location_data:
                    location, _ = Location.objects.get_or_create(
                        state=location_data.get('state', ''),
                        district=location_data.get('district'),
                        defaults={
                            'state': location_data.get('state', ''),
                            'district': location_data.get('district')
                        }
                    )

                # Create product
                product = Product.objects.create(
                    name=name,
                    product_code=product_code,
                    description=description or '',
                    category=category,
                    seller=seller,
                    location=location,
                    tag=tag,
                    price=price,
                    currency=currency,
                    availability=availability,
                    is_active=True
                )

                # Store extra_info key-value as ProductSpecification so buyer
                # product detail API can show specs (Indiamart-style listing).
                for key, value in extra_info.items():
                    if value is not None and value != '':
                        ProductSpecification.objects.create(
                            product=product,
                            key=str(key),
                            value=str(value)
                        )

                # Create seller product with extra_info
                seller_product = SellerProduct.objects.create(
                    product=product,
                    seller=seller,
                    status='listed',
                    extra_info=extra_info
                )

                # Handle images if provided
                if images:
                    ProductService._save_product_images(
                        product,
                        images
                    )

                logger.info(
                    f"Created seller product: {product_code} "
                    f"by seller {seller.name}"
                )

                return seller_product

        except Exception as e:
            logger.error(
                f"Error creating seller product: {str(e)}",
                exc_info=True
            )
            raise

    @staticmethod
    def _generate_product_code(category_code):
        """
        Generate unique product code.

        Args:
            category_code: Category code

        Returns:
            str: Unique product code
        """
        import random
        import string

        # Format: CAT001-PROD-XXXXXX
        random_suffix = ''.join(
            random.choices(
                string.ascii_uppercase + string.digits,
                k=6
            )
        )
        product_code = f"{category_code}-PROD-{random_suffix}"

        # Ensure uniqueness
        while Product.objects.filter(
            product_code=product_code
        ).exists():
            random_suffix = ''.join(
                random.choices(
                    string.ascii_uppercase + string.digits,
                    k=6
                )
            )
            product_code = f"{category_code}-PROD-{random_suffix}"

        return product_code

    @staticmethod
    def _save_product_images(product, images):
        """
        Save product images.

        Args:
            product: Product instance
            images: List of image files
        """
        for index, image_file in enumerate(images):
            # For now, store image URL
            # In production, upload to cloud storage (S3, etc.)
            # and get URL
            image_url = ProductService._upload_image(image_file)

            ProductImage.objects.create(
                product=product,
                image_url=image_url,
                order=index
            )

    @staticmethod
    def _upload_image(image_file):
        """
        Upload image and return URL.

        Args:
            image_file: Image file

        Returns:
            str: Image URL

        Note:
            This is a placeholder. In production, implement actual
            image upload to cloud storage (AWS S3, Cloudinary, etc.)
        """
        # TODO: Implement actual image upload
        # For now, return a placeholder URL
        # In production, upload to S3/Cloudinary and return URL
        import uuid
        return f"https://example.com/images/{uuid.uuid4()}.jpg"

