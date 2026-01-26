"""
Service for seller product creation and management.
"""

import logging
import uuid
from django.db import transaction
from django.utils import timezone
from olmachine_products.models import (
    Category,
    Product,
    Location,
    ProductImage,
    Seller
)
from olmachine_seller_portal.models import SellerProduct
from olmachine_seller_portal.services.form_service import FormService

logger = logging.getLogger(__name__)


class ProductService:
    """Service for seller product management."""

    @staticmethod
    def create_seller_product(
        seller,
        category_code,
        form_data,
        images=None,
        location_data=None
    ):
        """
        Create a product from seller form submission.

        Args:
            seller: Seller instance
            category_code: Category code
            form_data: Validated form data dictionary
            images: List of image files (optional)
            location_data: Location data dict (optional)

        Returns:
            SellerProduct: Created seller product

        Raises:
            ValidationError: If creation fails
        """
        try:
            with transaction.atomic():
                # Get category
                category = Category.objects.get(
                    category_code=category_code,
                    is_active=True
                )

                # Get form config and validate
                form_config = FormService.get_form_config(category_code)
                validated_data = FormService.validate_form_data(
                    form_config,
                    form_data
                )

                # Extract common product fields from form data
                product_name = validated_data.get('name', '')
                if not product_name:
                    raise ValueError("Product name is required")

                product_description = validated_data.get(
                    'description',
                    ''
                )
                product_price = validated_data.get('price')
                product_currency = validated_data.get('currency', 'INR')
                product_tag = validated_data.get('tag')
                product_availability = validated_data.get(
                    'availability',
                    'In Stock'
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
                    name=product_name,
                    product_code=product_code,
                    description=product_description,
                    category=category,
                    seller=seller,
                    location=location,
                    tag=product_tag,
                    price=product_price,
                    currency=product_currency,
                    availability=product_availability,
                    is_active=True  # Will be controlled by status
                )

                # Create product specifications from form data
                # (excluding common fields)
                common_fields = [
                    'name',
                    'description',
                    'price',
                    'currency',
                    'tag',
                    'availability'
                ]
                for key, value in validated_data.items():
                    if key not in common_fields and value:
                        from olmachine_products.models import (
                            ProductSpecification
                        )
                        ProductSpecification.objects.create(
                            product=product,
                            key=key,
                            value=str(value)
                        )

                # Create seller product
                seller_product = SellerProduct.objects.create(
                    product=product,
                    seller=seller,
                    status='listed',  # Direct listing (no approval yet)
                    form_data=validated_data
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

