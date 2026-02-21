"""
Views for olmachine_products app.
"""

import logging
from decimal import Decimal, InvalidOperation
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Exists, IntegerField, OuterRef, Q
from django.db.models.functions import Cast

from olmachine_products.constants import (
    PRODUCT_SPEC_CONDITION_KEY,
    PRODUCT_SPEC_YEAR_KEY,
)
from olmachine_products.models import (
    Category,
    Product,
    ProductSpecification,
    SavedSearch,
)
from olmachine_products.serializers import (
    CategoryDetailSerializer,
    CategoryProductDetailSerializer,
    ProductDetailsSerializer,
    ProductDetailSerializer,
    SavedSearchCreateSerializer,
    SavedSearchSerializer,
)
from olmachine_products.permissions import AllowAnyOrValidToken
from olmachine_products.services.recommendation_service import (
    RecommendationService
)
from olmachine_products.services.product_search_service import (
    get_product_queryset_for_search
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
        operation_summary="Get categories with hierarchy and recommendations",
        operation_description=(
            "Retrieve a list of active categories with hierarchy information. "
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
                        "categories_details": [
                                {
                                    "id": "uuid-string",
                                    "name": "Electronics",
                                    "category_code": "ELEC001",
                                    "description": "Category description",
                                    "level": 0,
                                    "parent_category": None,
                                    "parent_category_name": None,
                                    "order": 1,
                                    "image_url": "https://example.com/image.jpg"
                                },
                                {
                                    "id": "uuid-string",
                                    "name": "Mobile Phones",
                                    "category_code": "MOB001",
                                    "description": "Mobile phone category",
                                    "level": 1,
                                    "parent_category": "ELEC001",
                                    "parent_category_name": "Electronics",
                                    "order": 1,
                                    "image_url": "https://example.com/mobile.jpg"
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
            # Get active categories (no products needed)
            categories = Category.objects.filter(
                is_active=True
            ).select_related(
                'parent_category'
            ).order_by('level', 'order', 'name')[offset:offset + limit]

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

            return success_response(
                data={
                    'categories_details': serializer.data,
                    'recommended_products': recommended_products
                },
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
            # If category has children, include products from all descendant leaf categories
            if category.is_leaf_category():
                # Leaf category - get products directly assigned
                product_categories = [category]
            else:
                # Parent category - get all descendant leaf categories
                descendant_ids = category.get_all_descendant_ids()
                # Get all categories in the descendant tree
                all_descendants = Category.objects.filter(
                    id__in=descendant_ids,
                    is_active=True
                )
                # Filter to only leaf categories (those with no active children)
                leaf_categories = [
                    cat for cat in all_descendants
                    if cat.is_leaf_category()
                ]
                product_categories = leaf_categories if leaf_categories else [category]

            # Get products from all relevant categories
            products = Product.objects.filter(
                category__in=product_categories,
                is_active=True
            ).select_related(
                'seller',
                'location',
                'category'
            ).prefetch_related(
                'images',
                'specifications'
            ).order_by('-created_at')[offset:offset + limit]

            # Get total count
            total_count = Product.objects.filter(
                category__in=product_categories,
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


SORT_CHOICES = ('newest_first', 'price_asc', 'price_desc')
DEFAULT_LIMIT = 10
MAX_LIMIT = 100


class ProductListingsSearchView(APIView):
    """
    POST /api/marketplace/product_listings/search/v1/

    Search and filter products. All filters and pagination in request body (JSON).
    Returns products_details, total_count, and breadcrumbs when category_code
    is present.
    """

    permission_classes = [AllowAnyOrValidToken]

    @swagger_auto_schema(
        operation_summary="Search and filter product listings",
        operation_description=(
            "Search and filter products by category, price, condition, "
            "location, year, and text. All parameters in request body (JSON). "
            "Returns products_details, total_count, and breadcrumbs when "
            "category_code is provided."
        ),
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'category_code': openapi.Schema(
                    type=openapi.TYPE_STRING, description='Category code'
                ),
                'min_price': openapi.Schema(
                    type=openapi.TYPE_NUMBER, description='Min price'
                ),
                'max_price': openapi.Schema(
                    type=openapi.TYPE_NUMBER, description='Max price'
                ),
                'condition': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Condition (e.g. Excellent, Good, Fair)'
                ),
                'state': openapi.Schema(type=openapi.TYPE_STRING),
                'district': openapi.Schema(type=openapi.TYPE_STRING),
                'location_search': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Text search on state/district'
                ),
                'year_from': openapi.Schema(
                    type=openapi.TYPE_INTEGER, description='Min year'
                ),
                'year_to': openapi.Schema(
                    type=openapi.TYPE_INTEGER, description='Max year'
                ),
                'sort': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=list(SORT_CHOICES),
                    description='Sort order'
                ),
                'search': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Text search on name/description'
                ),
                'limit': openapi.Schema(
                    type=openapi.TYPE_INTEGER, default=DEFAULT_LIMIT
                ),
                'offset': openapi.Schema(
                    type=openapi.TYPE_INTEGER, default=0
                ),
            },
        ),
        responses={
            200: openapi.Response(
                description="Success",
                examples={
                    "application/json": {
                        "data": {
                            "products_details": [],
                            "total_count": "42",
                            "breadcrumbs": [
                                {"name": "Cat", "category_code": "C1"}
                            ],
                        }
                    }
                },
            ),
            400: openapi.Response(description="Bad request"),
            401: openapi.Response(description="Unauthorized"),
            500: openapi.Response(description="Server error"),
        },
        tags=['Products'],
    )
    def post(self, request):
        """Handle POST with JSON body: filters, sort, search, limit, offset."""
        data = request.data if isinstance(request.data, dict) else {}

        # Pagination
        limit = data.get('limit', DEFAULT_LIMIT)
        offset = data.get('offset', 0)
        try:
            limit = int(limit)
            if limit < 1 or limit > MAX_LIMIT:
                return error_response(
                    message=f"Invalid limit. Must be between 1 and {MAX_LIMIT}",
                    res_status="INVALID_LIMIT",
                    http_status_code=status.HTTP_400_BAD_REQUEST
                )
        except (TypeError, ValueError):
            return error_response(
                message="Invalid limit",
                res_status="INVALID_LIMIT",
                http_status_code=status.HTTP_400_BAD_REQUEST
            )
        try:
            offset = int(offset)
            if offset < 0:
                return error_response(
                    message="Invalid offset. Must be >= 0",
                    res_status="INVALID_OFFSET",
                    http_status_code=status.HTTP_400_BAD_REQUEST
                )
        except (TypeError, ValueError):
            return error_response(
                message="Invalid offset",
                res_status="INVALID_OFFSET",
                http_status_code=status.HTTP_400_BAD_REQUEST
            )

        sort = data.get('sort', 'newest_first')
        if sort not in SORT_CHOICES:
            return error_response(
                message=f"Invalid sort. Must be one of {SORT_CHOICES}",
                res_status="INVALID_SORT",
                http_status_code=status.HTTP_400_BAD_REQUEST
            )

        # Optional numeric validation
        min_price = data.get('min_price')
        max_price = data.get('max_price')
        year_from = data.get('year_from')
        year_to = data.get('year_to')
        if min_price is not None:
            try:
                min_price = Decimal(str(min_price))
                if min_price < 0:
                    raise ValueError("min_price must be >= 0")
            except (TypeError, ValueError, InvalidOperation):
                return error_response(
                    message="Invalid min_price",
                    res_status="INVALID_MIN_PRICE",
                    http_status_code=status.HTTP_400_BAD_REQUEST
                )
        if max_price is not None:
            try:
                max_price = Decimal(str(max_price))
                if max_price < 0:
                    raise ValueError("max_price must be >= 0")
            except (TypeError, ValueError, InvalidOperation):
                return error_response(
                    message="Invalid max_price",
                    res_status="INVALID_MAX_PRICE",
                    http_status_code=status.HTTP_400_BAD_REQUEST
                )
        if min_price is not None and max_price is not None and min_price > max_price:
            return error_response(
                message="min_price must be <= max_price",
                res_status="INVALID_PRICE_RANGE",
                http_status_code=status.HTTP_400_BAD_REQUEST
            )
        if year_from is not None:
            try:
                year_from = int(year_from)
                if year_from < 0:
                    raise ValueError("year_from must be >= 0")
            except (TypeError, ValueError):
                return error_response(
                    message="Invalid year_from",
                    res_status="INVALID_YEAR_FROM",
                    http_status_code=status.HTTP_400_BAD_REQUEST
                )
        if year_to is not None:
            try:
                year_to = int(year_to)
                if year_to < 0:
                    raise ValueError("year_to must be >= 0")
            except (TypeError, ValueError):
                return error_response(
                    message="Invalid year_to",
                    res_status="INVALID_YEAR_TO",
                    http_status_code=status.HTTP_400_BAD_REQUEST
                )
        if (year_from is not None and year_to is not None and
                year_from > year_to):
            return error_response(
                message="year_from must be <= year_to",
                res_status="INVALID_YEAR_RANGE",
                http_status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            category = None
            product_categories = None
            category_code = data.get('category_code')
            if category_code:
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
                if category.is_leaf_category():
                    product_categories = [category]
                else:
                    descendant_ids = category.get_all_descendant_ids()
                    all_descendants = Category.objects.filter(
                        id__in=descendant_ids,
                        is_active=True
                    )
                    leaf_categories = [
                        c for c in all_descendants
                        if c.is_leaf_category()
                    ]
                    product_categories = (
                        leaf_categories if leaf_categories else [category]
                    )

                if request.user and request.user.is_authenticated:
                    RecommendationService.track_category_view(
                        user=request.user,
                        category=category
                    )

            queryset = Product.objects.filter(is_active=True)
            if product_categories is not None:
                queryset = queryset.filter(category__in=product_categories)

            if min_price is not None:
                queryset = queryset.filter(price__gte=min_price)
            if max_price is not None:
                queryset = queryset.filter(price__lte=max_price)

            condition = data.get('condition')
            if condition and isinstance(condition, str) and condition.strip():
                condition_subquery = ProductSpecification.objects.filter(
                    product_id=OuterRef('pk'),
                    key=PRODUCT_SPEC_CONDITION_KEY,
                    value=condition.strip()
                )
                queryset = queryset.filter(Exists(condition_subquery))

            if year_from is not None or year_to is not None:
                year_subquery = ProductSpecification.objects.filter(
                    product_id=OuterRef('pk'),
                    key=PRODUCT_SPEC_YEAR_KEY
                ).annotate(
                    year_int=Cast('value', IntegerField())
                )
                if year_from is not None and year_to is not None:
                    year_subquery = year_subquery.filter(
                        year_int__gte=year_from,
                        year_int__lte=year_to
                    )
                elif year_from is not None:
                    year_subquery = year_subquery.filter(
                        year_int__gte=year_from
                    )
                else:
                    year_subquery = year_subquery.filter(
                        year_int__lte=year_to
                    )
                queryset = queryset.filter(Exists(year_subquery))

            state = data.get('state')
            district = data.get('district')
            location_search = data.get('location_search')
            if state and isinstance(state, str):
                queryset = queryset.filter(
                    location__state__iexact=state.strip()
                )
            if district and isinstance(district, str):
                queryset = queryset.filter(
                    location__district__iexact=district.strip()
                )
            if location_search and isinstance(location_search, str) and location_search.strip():
                term = location_search.strip()
                queryset = queryset.filter(
                    Q(location__state__icontains=term) |
                    Q(location__district__icontains=term)
                )

            search_term = data.get('search')
            if search_term and isinstance(search_term, str):
                queryset = get_product_queryset_for_search(
                    queryset, search_term
                )

            if sort == 'newest_first':
                queryset = queryset.order_by('-created_at')
            elif sort == 'price_asc':
                queryset = queryset.order_by('price')
            else:
                queryset = queryset.order_by('-price')

            total_count = queryset.count()
            queryset = queryset.select_related(
                'seller', 'location', 'category'
            ).prefetch_related('images', 'specifications')
            products = queryset[offset:offset + limit]

            serializer = CategoryProductDetailSerializer(products, many=True)
            response_data = {
                'products_details': serializer.data,
                'total_count': str(total_count),
            }

            if category is not None:
                ancestors = category.get_ancestors()
                breadcrumbs = [
                    {'name': c.name, 'category_code': c.category_code}
                    for c in ancestors
                ]
                breadcrumbs.append({
                    'name': category.name,
                    'category_code': category.category_code
                })
                response_data['breadcrumbs'] = breadcrumbs

            return success_response(
                data=response_data,
                http_status_code=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"Error in product listings search: {str(e)}")
            return error_response(
                message="Error searching products",
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


class SavedSearchListCreateView(APIView):
    """
    GET  /api/marketplace/saved_searches/ — list current user's saved searches
    POST /api/marketplace/saved_searches/ — create a saved search
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="List saved searches",
        operation_description="List saved searches for the authenticated user.",
        responses={
            200: openapi.Response(
                description="Success",
                examples={
                    "application/json": {
                        "data": {
                            "saved_searches": [
                                {
                                    "id": "uuid",
                                    "name": "My search",
                                    "category_code": "CNC001",
                                    "query_params": {},
                                    "created_at": "2025-01-01T00:00:00Z"
                                }
                            ]
                        }
                    }
                },
            ),
            401: openapi.Response(description="Unauthorized"),
        },
        tags=['Saved Search'],
    )
    def get(self, request):
        """List current user's saved searches."""
        try:
            qs = SavedSearch.objects.filter(
                user=request.user
            ).order_by('-created_at')
            serializer = SavedSearchSerializer(qs, many=True)
            return success_response(
                data={'saved_searches': serializer.data},
                http_status_code=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Error listing saved searches: {str(e)}")
            return error_response(
                message="Error listing saved searches",
                res_status="ERROR",
                http_status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_summary="Create saved search",
        operation_description="Create a saved search for the authenticated user.",
        request_body=SavedSearchCreateSerializer,
        responses={
            201: openapi.Response(
                description="Created",
                examples={
                    "application/json": {
                        "data": {
                            "id": "uuid",
                            "name": "My search",
                            "category_code": "CNC001",
                            "query_params": {},
                            "created_at": "2025-01-01T00:00:00Z"
                        }
                    }
                },
            ),
            400: openapi.Response(description="Bad request"),
            401: openapi.Response(description="Unauthorized"),
        },
        tags=['Saved Search'],
    )
    def post(self, request):
        """Create a saved search."""
        serializer = SavedSearchCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message="Invalid payload",
                res_status="INVALID_PAYLOAD",
                http_status_code=status.HTTP_400_BAD_REQUEST
            )
        data = serializer.validated_data
        try:
            saved_search = SavedSearch.objects.create(
                user=request.user,
                name=data.get('name') or None,
                category_code=data.get('category_code') or None,
                query_params=data.get('query_params') or {}
            )
            out = SavedSearchSerializer(saved_search)
            return success_response(
                data=out.data,
                http_status_code=status.HTTP_201_CREATED
            )
        except Exception as e:
            logger.error(f"Error creating saved search: {str(e)}")
            return error_response(
                message="Error creating saved search",
                res_status="ERROR",
                http_status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SavedSearchDetailView(APIView):
    """
    DELETE /api/marketplace/saved_searches/<id>/ — delete a saved search
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Delete saved search",
        operation_description="Delete a saved search (must own it).",
        responses={
            204: openapi.Response(description="No content"),
            404: openapi.Response(description="Not found"),
            401: openapi.Response(description="Unauthorized"),
        },
        tags=['Saved Search'],
    )
    def delete(self, request, saved_search_id):
        """Delete a saved search by id."""
        try:
            saved_search = SavedSearch.objects.filter(
                id=saved_search_id,
                user=request.user
            ).first()
            if not saved_search:
                return error_response(
                    message="Saved search not found",
                    res_status="NOT_FOUND",
                    http_status_code=status.HTTP_404_NOT_FOUND
                )
            saved_search.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"Error deleting saved search: {str(e)}")
            return error_response(
                message="Error deleting saved search",
                res_status="ERROR",
                http_status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

