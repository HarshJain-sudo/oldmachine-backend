"""
Views for olmachine_products app.
"""

import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from olmachine_products.models import Category, Product
from olmachine_products.serializers import (
    CategoryDetailSerializer,
    CategoryProductDetailSerializer,
    ProductDetailsSerializer,
    ProductDetailSerializer
)
from olmachine_products.permissions import AllowAnyOrValidToken
from olmachine_products.services.recommendation_service import (
    RecommendationService
)
from oldmachine_backend.utils.response_utils import (
    success_response,
    error_response
)

logger = logging.getLogger(__name__)


class CategoriesDetailsView(APIView):
    """
    API view for getting categories with products and recommendations.

    GET /api/marketplace/categories_details/get/v1/
    
    Public endpoint. Shows personalized recommendations if user is
    authenticated.
    
    Returns 401 if invalid access token is provided.
    """

    permission_classes = [AllowAnyOrValidToken]

    @swagger_auto_schema(
        operation_summary="Get categories with products and recommendations",
        operation_description=(
            "Retrieve a list of active categories with their products. "
            "If a valid access token is provided, personalized "
            "recommendations based on user's viewing history will be "
            "included. Returns 401 if an invalid access token is provided."
        ),
        manual_parameters=[
            openapi.Parameter(
                'limit',
                openapi.IN_QUERY,
                description="Number of categories to return (1-100)",
                type=openapi.TYPE_INTEGER,
                default=10
            ),
            openapi.Parameter(
                'offset',
                openapi.IN_QUERY,
                description="Number of categories to skip",
                type=openapi.TYPE_INTEGER,
                default=0
            ),
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="Bearer token (optional). Format: 'Bearer {token}'",
                type=openapi.TYPE_STRING
            ),
        ],
        responses={
            200: openapi.Response(
                description="Successfully retrieved categories",
                examples={
                    "application/json": {
                        "data": {
                            "categories_details": [
                                {
                                    "name": "Category Name",
                                    "category_code": "CAT001",
                                    "description": "Category description",
                                    "order": 1,
                                    "image_url": "https://example.com/image.jpg",
                                    "products_details": [
                                        {
                                            "name": "Product Name",
                                            "product_code": "PROD001",
                                            "image_url": "https://example.com/product.jpg",
                                            "extra_config": "Key: Value"
                                        }
                                    ]
                                }
                            ],
                            "recommended_products": [
                                {
                                    "category_name": "Category Name",
                                    "category_code": "CAT001",
                                    "category_image_url": "https://example.com/image.jpg",
                                    "products": [
                                        {
                                            "name": "Product Name",
                                            "product_code": "PROD001",
                                            "image_url": "https://example.com/product.jpg"
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                }
            ),
            400: openapi.Response(
                description="Bad request - Invalid parameters"
            ),
            401: openapi.Response(
                description="Unauthorized - Invalid access token"
            ),
            500: openapi.Response(
                description="Internal server error"
            ),
        },
        tags=['Products']
    )
    def get(self, request):
        """
        Get list of categories with their products and recommended products.

        Args:
            request: HTTP request object

        Returns:
            Response: Categories details and recommendations on success
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

            # Get recommended products based on user's viewing history
            # Only if user is authenticated
            recommended_products = []
            if request.user and request.user.is_authenticated:
                recommended_data = (
                    RecommendationService.get_recommended_products(
                        user=request.user,
                        products_per_category=3
                    )
                )

                # Serialize recommended products
                for rec_data in recommended_data:
                    category = rec_data['category']
                    products = rec_data['products']
                    # Use ProductDetailSerializer for recommended products
                    product_serializer = ProductDetailSerializer(
                        products, many=True
                    )
                    recommended_products.append({
                        'category_name': category.name,
                        'category_code': category.category_code,
                        'category_image_url': category.image_url,
                        'products': product_serializer.data
                    })

            response_data = {
                'categories_details': serializer.data,
                'recommended_products': recommended_products
            }

            return success_response(
                data=response_data,
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
    
    Public endpoint. Tracks user's category views for recommendations
    if valid access token is provided.
    
    Returns 401 if invalid access token is provided.
    """

    permission_classes = [AllowAnyOrValidToken]

    @swagger_auto_schema(
        operation_summary="Get products in a specific category",
        operation_description=(
            "Retrieve a list of products for a specific category. "
            "If a valid access token is provided, the category view "
            "will be tracked for personalized recommendations. "
            "Returns 401 if an invalid access token is provided."
        ),
        manual_parameters=[
            openapi.Parameter(
                'category_code',
                openapi.IN_QUERY,
                description="Category code to filter products",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'limit',
                openapi.IN_QUERY,
                description="Number of products to return (1-100)",
                type=openapi.TYPE_INTEGER,
                default=10
            ),
            openapi.Parameter(
                'offset',
                openapi.IN_QUERY,
                description="Number of products to skip",
                type=openapi.TYPE_INTEGER,
                default=0
            ),
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="Bearer token (optional). Format: 'Bearer {token}'",
                type=openapi.TYPE_STRING
            ),
        ],
        responses={
            200: openapi.Response(
                description="Successfully retrieved products",
                examples={
                    "application/json": {
                        "data": {
                            "products_details": [
                                {
                                    "name": "Product Name",
                                    "product_code": "PROD001",
                                    "seller_details": {"name": "Seller Name"},
                                    "tag": "New",
                                    "image_urls": ["https://example.com/image.jpg"],
                                    "location_details": {
                                        "state": "State",
                                        "district": "District"
                                    },
                                    "product_specifications": {
                                        "key": "value"
                                    }
                                }
                            ],
                            "total_count": "50"
                        }
                    }
                }
            ),
            400: openapi.Response(
                description="Bad request - Invalid parameters"
            ),
            401: openapi.Response(
                description="Unauthorized - Invalid access token"
            ),
            500: openapi.Response(
                description="Internal server error"
            ),
        },
        tags=['Products']
    )
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

            # Track user's category view for recommendations
            # Only if user is authenticated (valid token provided)
            if request.user and request.user.is_authenticated:
                RecommendationService.track_category_view(
                    user=request.user,
                    category=category
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
    
    Public endpoint. Tracks user's category views for recommendations
    if valid access token is provided.
    
    Returns 401 if invalid access token is provided.
    """

    permission_classes = [AllowAnyOrValidToken]

    @swagger_auto_schema(
        operation_summary="Get detailed product information",
        operation_description=(
            "Retrieve detailed information about a specific product. "
            "If a valid access token is provided, the product's category "
            "view will be tracked for personalized recommendations. "
            "Returns 401 if an invalid access token is provided."
        ),
        manual_parameters=[
            openapi.Parameter(
                'product_code',
                openapi.IN_PATH,
                description="Product code",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="Bearer token (optional). Format: 'Bearer {token}'",
                type=openapi.TYPE_STRING
            ),
        ],
        responses={
            200: openapi.Response(
                description="Successfully retrieved product details",
                examples={
                    "application/json": {
                        "data": {
                            "name": "Product Name",
                            "product_code": "PROD001",
                            "description": "Product description",
                            "seller_details": {"name": "Seller Name"},
                            "tag": "New",
                            "image_urls": ["https://example.com/image.jpg"],
                            "location_details": {
                                "state": "State",
                                "district": "District"
                            },
                            "product_specifications": {
                                "key": "value"
                            },
                            "price": "1000.00",
                            "currency": "USD",
                            "availability": True
                        }
                    }
                }
            ),
            404: openapi.Response(
                description="Product not found"
            ),
            401: openapi.Response(
                description="Unauthorized - Invalid access token"
            ),
            500: openapi.Response(
                description="Internal server error"
            ),
        },
        tags=['Products']
    )
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

            # Track user's category view for recommendations
            # Only if user is authenticated (valid token provided)
            # (tracking the category of the product being viewed)
            if request.user and request.user.is_authenticated:
                RecommendationService.track_category_view(
                    user=request.user,
                    category=product.category
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

