"""
Views for olmachine_products app.
"""

import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from olmachine_products.models import Category, Product
from olmachine_products.serializers import (
    CategoryDetailSerializer,
    CategoryProductDetailSerializer,
    ProductDetailsSerializer
)
from oldmachine_backend.utils.response_utils import (
    success_response,
    error_response
)

logger = logging.getLogger(__name__)


class CategoriesDetailsView(APIView):
    """
    API view for getting categories with products.

    GET /api/marketplace/categories_details/get/v1/
    """

    permission_classes = [AllowAny]

    def get(self, request):
        """
        Get list of categories with their products.

        Args:
            request: HTTP request object

        Returns:
            Response: Categories details on success
        """
        # Get pagination parameters
        limit = request.query_params.get('limit', '10')
        offset = request.query_params.get('offset', '0')

        # Validate limit
        try:
            limit = int(limit)
            if limit < 1 or limit > 100:
                return error_response(
                    message="Invalid limit. Must be between 1 and 100",
                    res_status="INVALID_LIMIT",
                    http_status_code=status.HTTP_400_BAD_REQUEST
                )
        except ValueError:
            return error_response(
                message="Invalid limit",
                res_status="INVALID_LIMIT",
                http_status_code=status.HTTP_400_BAD_REQUEST
            )

        # Validate offset
        try:
            offset = int(offset)
            if offset < 0:
                return error_response(
                    message="Invalid offset. Must be >= 0",
                    res_status="INVALID_OFFSET",
                    http_status_code=status.HTTP_400_BAD_REQUEST
                )
        except ValueError:
            return error_response(
                message="Invalid offset",
                res_status="INVALID_OFFSET",
                http_status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Get active categories with products
            categories = Category.objects.filter(
                is_active=True
            ).prefetch_related(
                'products__images',
                'products__specifications'
            ).filter(
                products__is_active=True
            ).distinct().order_by('order', 'name')[offset:offset + limit]

            serializer = CategoryDetailSerializer(categories, many=True)

            return success_response(
                data={'categories_details': serializer.data},
                http_status_code=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"Error fetching categories: {str(e)}")
            return error_response(
                message="Error fetching categories",
                res_status="ERROR",
                http_status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CategoryProductsDetailsView(APIView):
    """
    API view for getting products in a category.

    GET /api/marketplace/category_products_details/get/v1/
    """

    permission_classes = [AllowAny]

    def get(self, request):
        """
        Get list of products for a specific category.

        Args:
            request: HTTP request object

        Returns:
            Response: Products details on success
        """
        category_code = request.query_params.get('category_code')
        limit = request.query_params.get('limit', '10')
        offset = request.query_params.get('offset', '0')

        # Validate category_code
        if not category_code:
            return error_response(
                message="Invalid category code",
                res_status="INVALID_CATEGORY_CODE",
                http_status_code=status.HTTP_400_BAD_REQUEST
            )

        # Validate limit
        try:
            limit = int(limit)
            if limit < 1 or limit > 100:
                return error_response(
                    message="Invalid limit. Must be between 1 and 100",
                    res_status="INVALID_LIMIT",
                    http_status_code=status.HTTP_400_BAD_REQUEST
                )
        except ValueError:
            return error_response(
                message="Invalid limit",
                res_status="INVALID_LIMIT",
                http_status_code=status.HTTP_400_BAD_REQUEST
            )

        # Validate offset
        try:
            offset = int(offset)
            if offset < 0:
                return error_response(
                    message="Invalid offset. Must be >= 0",
                    res_status="INVALID_OFFSET",
                    http_status_code=status.HTTP_400_BAD_REQUEST
                )
        except ValueError:
            return error_response(
                message="Invalid offset",
                res_status="INVALID_OFFSET",
                http_status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Get category
            try:
                category = Category.objects.get(
                    category_code=category_code,
                    is_active=True
                )
            except Category.DoesNotExist:
                return error_response(
                    message="Invalid category code",
                    res_status="INVALID_CATEGORY_CODE",
                    http_status_code=status.HTTP_400_BAD_REQUEST
                )

            # Get products for category
            products = Product.objects.filter(
                category=category,
                is_active=True
            ).select_related(
                'seller',
                'location'
            ).prefetch_related(
                'images',
                'specifications'
            ).order_by('-created_at')[offset:offset + limit]

            # Get total count
            total_count = Product.objects.filter(
                category=category,
                is_active=True
            ).count()

            serializer = CategoryProductDetailSerializer(products, many=True)

            return success_response(
                data={
                    'products_details': serializer.data,
                    'total_count': str(total_count)
                },
                http_status_code=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"Error fetching category products: {str(e)}")
            return error_response(
                message="Error fetching category products",
                res_status="ERROR",
                http_status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProductDetailsView(APIView):
    """
    API view for getting product details.

    GET /api/marketplace/product_details/get/v1/{product_code}/
    """

    permission_classes = [AllowAny]

    def get(self, request, product_code):
        """
        Get detailed information about a specific product.

        Args:
            request: HTTP request object
            product_code: Product code

        Returns:
            Response: Product details on success
        """
        try:
            product = Product.objects.filter(
                product_code=product_code,
                is_active=True
            ).select_related(
                'seller',
                'location',
                'category'
            ).prefetch_related(
                'images',
                'specifications'
            ).first()

            if not product:
                return error_response(
                    message="Product not found",
                    res_status="PRODUCT_NOT_FOUND",
                    http_status_code=status.HTTP_404_NOT_FOUND
                )

            serializer = ProductDetailsSerializer(product)

            return success_response(
                data=serializer.data,
                http_status_code=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"Error fetching product details: {str(e)}")
            return error_response(
                message="Error fetching product details",
                res_status="ERROR",
                http_status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

