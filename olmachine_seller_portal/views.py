"""
Views for olmachine_seller_portal app.
"""

import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.shortcuts import get_object_or_404
from olmachine_products.models import Category
from olmachine_seller_portal.models import (
    CategoryFormConfig,
    SellerProfile,
    SellerProduct
)
from olmachine_seller_portal.models import MAX_CATEGORY_DEPTH
from olmachine_seller_portal.serializers import (
    CategoryFormConfigSerializer,
    SellerProductSerializer,
    SellerProductCreateSerializer,
    SellerProductUpdateSerializer,
)
from olmachine_seller_portal.permissions import IsSeller
from olmachine_seller_portal.services.product_service import ProductService
from oldmachine_backend.utils.response_utils import (
    success_response,
    error_response
)

logger = logging.getLogger(__name__)

# --- Swagger response schemas (so response objects are defined in UI) ---

_category_item_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    description="Single category in tree",
    properties={
        'category_code': openapi.Schema(type=openapi.TYPE_STRING, description='Unique category code'),
        'category_name': openapi.Schema(type=openapi.TYPE_STRING, description='Display name'),
        'description': openapi.Schema(type=openapi.TYPE_STRING),
        'image_url': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, nullable=True),
        'level': openapi.Schema(type=openapi.TYPE_INTEGER, description='Depth in tree (0=root)'),
        'parent_category_code': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
        'parent_category_name': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
        'full_path': openapi.Schema(type=openapi.TYPE_STRING, description='e.g. Electronics > Phones'),
        'has_children': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='True if has sub-categories'),
        'is_leaf': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='True if no children; use form config'),
    },
    required=['category_code', 'category_name', 'level', 'has_children', 'is_leaf']
)

_categories_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    description="Response with list of categories",
    properties={
        'categories': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            description='List of categories',
            items=_category_item_schema
        )
    },
    required=['categories']
)

_form_field_schema_item = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    description="Form field definition for frontend",
    properties={
        'field_name': openapi.Schema(type=openapi.TYPE_STRING, description='Key for extra_info on submit'),
        'field_label': openapi.Schema(type=openapi.TYPE_STRING),
        'field_type': openapi.Schema(type=openapi.TYPE_STRING, enum=['text', 'number', 'textarea', 'select', 'radio', 'checkbox', 'date', 'email', 'url']),
        'is_required': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'order': openapi.Schema(type=openapi.TYPE_INTEGER),
        'options': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT), description='For select/radio'),
        'placeholder': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
        'help_text': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
    }
)

_form_config_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    description="Form configuration for leaf category",
    properties={
        'id': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID),
        'category': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID),
        'category_code': openapi.Schema(type=openapi.TYPE_STRING),
        'category_name': openapi.Schema(type=openapi.TYPE_STRING),
        'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'schema': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            description='Field definitions for frontend to render form',
            items=_form_field_schema_item
        ),
        'is_leaf': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Always true'),
    },
    required=['category_code', 'category_name', 'schema', 'is_leaf']
)

_error_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'response': openapi.Schema(type=openapi.TYPE_STRING, description='Error message'),
        'http_status_code': openapi.Schema(type=openapi.TYPE_INTEGER),
        'res_status': openapi.Schema(type=openapi.TYPE_STRING, description='Machine-readable status'),
    },
    required=['response', 'http_status_code', 'res_status']
)

_create_product_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    description="Created seller product",
    properties={
        'id': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID),
        'product': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID),
        'product_details': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            description='Nested product (name, product_code, price, product_specifications, etc.)'
        ),
        'seller': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID),
        'seller_name': openapi.Schema(type=openapi.TYPE_STRING),
        'status': openapi.Schema(type=openapi.TYPE_STRING, enum=['draft', 'pending_approval', 'approved', 'rejected', 'listed']),
        'rejection_reason': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
        'approved_by': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
        'approved_by_name': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
        'approved_at': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
        'extra_info': openapi.Schema(type=openapi.TYPE_OBJECT, description='Key-value from form'),
        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
        'updated_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
    },
    required=['id', 'product', 'status', 'extra_info']
)


_seller_products_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    description="Paginated seller products",
    properties={
        'products': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=_create_product_response_schema
        ),
        'total_count': openapi.Schema(type=openapi.TYPE_STRING),
    },
    required=['products', 'total_count']
)


def _category_to_dict(cat):
    """Build category payload for tree APIs."""
    return {
        'category_code': cat.category_code,
        'category_name': cat.name,
        'description': cat.description or '',
        'image_url': cat.image_url,
        'level': cat.level,
        'parent_category_code': (
            cat.parent_category.category_code
            if cat.parent_category else None
        ),
        'parent_category_name': (
            cat.parent_category.name
            if cat.parent_category else None
        ),
        'full_path': cat.get_full_path(),
        'has_children': cat.sub_categories.filter(is_active=True).exists(),
        'is_leaf': cat.is_leaf_category(),
    }


def _get_limit_offset(request):
    """Validate and return pagination params."""
    limit = request.query_params.get('limit', '10')
    offset = request.query_params.get('offset', '0')
    try:
        limit = int(limit)
        if limit < 1 or limit > 100:
            raise ValueError
    except ValueError:
        return None, None, error_response(
            message="Invalid limit. Must be between 1 and 100",
            res_status="INVALID_LIMIT",
            http_status_code=status.HTTP_400_BAD_REQUEST
        )
    try:
        offset = int(offset)
        if offset < 0:
            raise ValueError
    except ValueError:
        return None, None, error_response(
            message="Invalid offset. Must be >= 0",
            res_status="INVALID_OFFSET",
            http_status_code=status.HTTP_400_BAD_REQUEST
        )
    return limit, offset, None


class RootCategoriesView(APIView):
    """
    List root categories (categories with no parent).
    Seller selects one, then uses children API to drill down (max 5 levels).

    GET /api/seller-portal/categories/roots/
    """

    permission_classes = [IsAuthenticated, IsSeller]

    @swagger_auto_schema(
        operation_summary="List root categories",
        operation_description=(
            "Get categories that have no parent. Seller selects one, then "
            "calls children API for that category. Drill down until a leaf "
            "category is selected (max 5 levels)."
        ),
        responses={
            200: openapi.Response(
                description="List of root categories",
                schema=_categories_response_schema
            ),
            401: openapi.Response(description="Unauthorized", schema=_error_response_schema),
        },
        tags=['Seller Portal']
    )
    def get(self, request):
        roots = Category.objects.filter(
            is_active=True,
            parent_category__isnull=True
        ).order_by('order', 'name')
        data = [_category_to_dict(c) for c in roots]
        return success_response(
            data={'categories': data},
            http_status_code=status.HTTP_200_OK
        )


class CategoryChildrenView(APIView):
    """
    List direct children of a category.
    Used to drill down the tree (max depth 5). When a category has no
    children, it is a leaf; use form config API for that category.

    GET /api/seller-portal/categories/children/<category_code>/
    """

    permission_classes = [IsAuthenticated, IsSeller]

    @swagger_auto_schema(
        operation_summary="List child categories",
        operation_description=(
            "Get direct sub-categories of the given category. "
            "Nested structure is allowed up to 5 levels. When the selected "
            "category has no children (is_leaf), use form config API."
        ),
        responses={
            200: openapi.Response(
                description="List of child categories",
                schema=_categories_response_schema
            ),
            404: openapi.Response(description="Category not found", schema=_error_response_schema),
            401: openapi.Response(description="Unauthorized", schema=_error_response_schema),
        },
        tags=['Seller Portal']
    )
    def get(self, request, category_code):
        category = get_object_or_404(
            Category,
            category_code=category_code,
            is_active=True
        )
        if category.level >= MAX_CATEGORY_DEPTH - 1:
            return success_response(
                data={'categories': []},
                http_status_code=status.HTTP_200_OK
            )
        children = category.sub_categories.filter(
            is_active=True
        ).order_by('order', 'name')
        data = [_category_to_dict(c) for c in children]
        return success_response(
            data={'categories': data},
            http_status_code=status.HTTP_200_OK
        )


class FormConfigView(APIView):
    """
    Get form configuration for a leaf category.
    Frontend uses schema (JSON) to render the form. When seller submits,
    send the filled key-value as extra_info in create product.

    GET /api/seller-portal/form/<category_code>/
    """

    permission_classes = [IsAuthenticated, IsSeller]

    @swagger_auto_schema(
        operation_summary="Get form config for category",
        operation_description=(
            "Returns form schema for the given category. Only available for "
            "leaf categories (no children). Schema is a JSON array of field "
            "definitions (field_name, field_label, field_type, is_required, "
            "order, options) for frontend to render the form. Submit values "
            "as extra_info when creating the product."
        ),
        responses={
            200: openapi.Response(
                description="Form configuration with schema",
                schema=_form_config_response_schema
            ),
            400: openapi.Response(description="Not a leaf category", schema=_error_response_schema),
            404: openapi.Response(description="Category or form config not found", schema=_error_response_schema),
            401: openapi.Response(description="Unauthorized", schema=_error_response_schema),
        },
        tags=['Seller Portal']
    )
    def get(self, request, category_code):
        category = get_object_or_404(
            Category,
            category_code=category_code,
            is_active=True
        )
        if not category.is_leaf_category():
            return error_response(
                message=(
                    "Form is only available for leaf categories. "
                    "Please select a sub-category."
                ),
                res_status="NOT_LEAF_CATEGORY",
                http_status_code=status.HTTP_400_BAD_REQUEST
            )
        try:
            form_config = CategoryFormConfig.objects.get(
                category=category,
                is_active=True
            )
        except CategoryFormConfig.DoesNotExist:
            return error_response(
                message="No form configuration found for this category.",
                res_status="FORM_CONFIG_NOT_FOUND",
                http_status_code=status.HTTP_404_NOT_FOUND
            )
        serializer = CategoryFormConfigSerializer(form_config)
        return success_response(
            data={
                **serializer.data,
                'is_leaf': True,
            },
            http_status_code=status.HTTP_200_OK
        )


class SellerProductListCreateView(APIView):
    """
    List and create seller products.

    GET /api/seller-portal/products/
    POST /api/seller-portal/products/
    """

    permission_classes = [IsAuthenticated, IsSeller]

    @swagger_auto_schema(
        operation_summary="List seller products",
        operation_description=(
            "List products created by the authenticated seller. Supports "
            "pagination and optional status filtering."
        ),
        manual_parameters=[
            openapi.Parameter(
                'status',
                openapi.IN_QUERY,
                description=(
                    "Optional status filter: draft, pending_approval, "
                    "approved, rejected, listed"
                ),
                type=openapi.TYPE_STRING,
                required=False
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
        ],
        responses={
            200: openapi.Response(
                description="Seller products fetched successfully",
                schema=_seller_products_response_schema
            ),
            400: openapi.Response(
                description="Bad request",
                schema=_error_response_schema
            ),
            401: openapi.Response(
                description="Unauthorized",
                schema=_error_response_schema
            ),
            404: openapi.Response(
                description="Seller profile not found",
                schema=_error_response_schema
            ),
        },
        tags=['Seller Portal']
    )
    def get(self, request):
        """List seller products for logged-in seller."""
        try:
            seller_profile = SellerProfile.objects.get(user=request.user)
        except SellerProfile.DoesNotExist:
            return error_response(
                message="Seller profile not found",
                res_status="SELLER_PROFILE_NOT_FOUND",
                http_status_code=status.HTTP_404_NOT_FOUND
            )

        limit, offset, error = _get_limit_offset(request)
        if error:
            return error

        status_filter = request.query_params.get('status')
        allowed_statuses = {choice[0] for choice in SellerProduct.STATUS_CHOICES}
        if status_filter and status_filter not in allowed_statuses:
            return error_response(
                message="Invalid status filter",
                res_status="INVALID_STATUS",
                http_status_code=status.HTTP_400_BAD_REQUEST
            )

        queryset = SellerProduct.objects.filter(
            seller=seller_profile.seller,
            product__is_active=True
        ).select_related(
            'product',
            'seller',
            'approved_by',
            'product__seller',
            'product__location',
            'product__category'
        ).prefetch_related(
            'product__images',
            'product__specifications'
        )

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        total_count = queryset.count()
        seller_products = queryset[offset:offset + limit]
        serializer = SellerProductSerializer(seller_products, many=True)

        return success_response(
            data={
                'products': serializer.data,
                'total_count': str(total_count)
            },
            http_status_code=status.HTTP_200_OK
        )

    @swagger_auto_schema(
        operation_summary="Create seller product",
        operation_description=(
            "Create a new product. Provide category_code, name, and optional "
            "description, price, currency, tag, availability, extra_info "
            "(JSON), location, and images."
        ),
        request_body=SellerProductCreateSerializer,
        responses={
            201: openapi.Response(
                description="Product created successfully",
                schema=_create_product_response_schema
            ),
            400: openapi.Response(
                description="Bad request",
                schema=_error_response_schema
            ),
            401: openapi.Response(
                description="Unauthorized",
                schema=_error_response_schema
            ),
            404: openapi.Response(
                description="Seller profile not found",
                schema=_error_response_schema
            ),
            500: openapi.Response(
                description="Server error",
                schema=_error_response_schema
            ),
        },
        tags=['Seller Portal']
    )
    def post(self, request):
        """Create seller product."""
        try:
            seller_profile = SellerProfile.objects.get(user=request.user)
            seller = seller_profile.seller
        except SellerProfile.DoesNotExist:
            return error_response(
                message="Seller profile not found",
                res_status="SELLER_PROFILE_NOT_FOUND",
                http_status_code=status.HTTP_404_NOT_FOUND
            )

        serializer = SellerProductCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message="Invalid product data",
                res_status="INVALID_DATA",
                http_status_code=status.HTTP_400_BAD_REQUEST
            )

        data = serializer.validated_data
        try:
            seller_product = ProductService.create_seller_product(
                seller=seller,
                category_code=data['category_code'],
                name=data['name'],
                description=data.get('description', ''),
                price=data.get('price'),
                currency=data.get('currency', 'INR'),
                tag=data.get('tag'),
                availability=data.get('availability', 'In Stock'),
                extra_info=data.get('extra_info') or {},
                images=request.FILES.getlist('images'),
                location_data=data.get('location')
            )
            response_serializer = SellerProductSerializer(seller_product)
            return success_response(
                data=response_serializer.data,
                http_status_code=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return error_response(
                message=str(e),
                res_status="VALIDATION_ERROR",
                http_status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error creating seller product: {str(e)}")
            return error_response(
                message="Error creating product",
                res_status="ERROR",
                http_status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SellerProductDetailView(APIView):
    """
    Retrieve, update, or de-list a seller product.

    GET /api/seller-portal/products/<seller_product_id>/
    PUT/PATCH /api/seller-portal/products/<seller_product_id>/
    DELETE /api/seller-portal/products/<seller_product_id>/
    """

    permission_classes = [IsAuthenticated, IsSeller]

    def _get_seller_product(self, request, seller_product_id):
        """Get seller product scoped to logged-in seller."""
        try:
            seller_profile = SellerProfile.objects.get(user=request.user)
        except SellerProfile.DoesNotExist:
            return None, error_response(
                message="Seller profile not found",
                res_status="SELLER_PROFILE_NOT_FOUND",
                http_status_code=status.HTTP_404_NOT_FOUND
            )

        seller_product = SellerProduct.objects.filter(
            id=seller_product_id,
            seller=seller_profile.seller,
            product__is_active=True
        ).select_related(
            'product',
            'seller',
            'approved_by',
            'product__seller',
            'product__location',
            'product__category'
        ).prefetch_related(
            'product__images',
            'product__specifications'
        ).first()

        if not seller_product:
            return None, error_response(
                message="Seller product not found",
                res_status="SELLER_PRODUCT_NOT_FOUND",
                http_status_code=status.HTTP_404_NOT_FOUND
            )
        return seller_product, None

    @swagger_auto_schema(
        operation_summary="Get seller product detail",
        responses={
            200: openapi.Response(
                description="Seller product details",
                schema=_create_product_response_schema
            ),
            401: openapi.Response(
                description="Unauthorized",
                schema=_error_response_schema
            ),
            404: openapi.Response(
                description="Not found",
                schema=_error_response_schema
            ),
        },
        tags=['Seller Portal']
    )
    def get(self, request, seller_product_id):
        """Get seller product details."""
        seller_product, error = self._get_seller_product(
            request=request,
            seller_product_id=seller_product_id
        )
        if error:
            return error

        serializer = SellerProductSerializer(seller_product)
        return success_response(
            data=serializer.data,
            http_status_code=status.HTTP_200_OK
        )

    @swagger_auto_schema(
        operation_summary="Update seller product",
        request_body=SellerProductUpdateSerializer,
        responses={
            200: openapi.Response(
                description="Seller product updated",
                schema=_create_product_response_schema
            ),
            400: openapi.Response(
                description="Bad request",
                schema=_error_response_schema
            ),
            401: openapi.Response(
                description="Unauthorized",
                schema=_error_response_schema
            ),
            404: openapi.Response(
                description="Not found",
                schema=_error_response_schema
            ),
        },
        tags=['Seller Portal']
    )
    def put(self, request, seller_product_id):
        """Full update of a seller product."""
        return self._update_product(
            request=request,
            seller_product_id=seller_product_id,
            partial=False
        )

    @swagger_auto_schema(
        operation_summary="Partial update seller product",
        request_body=SellerProductUpdateSerializer,
        responses={
            200: openapi.Response(
                description="Seller product updated",
                schema=_create_product_response_schema
            ),
            400: openapi.Response(
                description="Bad request",
                schema=_error_response_schema
            ),
            401: openapi.Response(
                description="Unauthorized",
                schema=_error_response_schema
            ),
            404: openapi.Response(
                description="Not found",
                schema=_error_response_schema
            ),
        },
        tags=['Seller Portal']
    )
    def patch(self, request, seller_product_id):
        """Partial update of a seller product."""
        return self._update_product(
            request=request,
            seller_product_id=seller_product_id,
            partial=True
        )

    def _update_product(self, request, seller_product_id, partial):
        """Handle put/patch update logic."""
        seller_product, error = self._get_seller_product(
            request=request,
            seller_product_id=seller_product_id
        )
        if error:
            return error

        serializer = SellerProductUpdateSerializer(
            instance=seller_product,
            data=request.data,
            partial=partial
        )
        if not serializer.is_valid():
            return error_response(
                message="Invalid product data",
                res_status="INVALID_DATA",
                http_status_code=status.HTTP_400_BAD_REQUEST
            )

        data = serializer.validated_data
        update_kwargs = {}
        if 'category_code' in data:
            update_kwargs['category_code'] = data.get('category_code')
        if 'name' in data:
            update_kwargs['name'] = data.get('name')
        if 'description' in data:
            update_kwargs['description'] = data.get('description')
        if 'price' in data:
            update_kwargs['price'] = data.get('price')
        if 'currency' in data:
            update_kwargs['currency'] = data.get('currency')
        if 'tag' in data:
            update_kwargs['tag'] = data.get('tag')
        if 'availability' in data:
            update_kwargs['availability'] = data.get('availability')
        if 'extra_info' in data:
            update_kwargs['extra_info'] = data.get('extra_info') or {}
        if 'location' in data:
            update_kwargs['location_data'] = data.get('location')
        if 'images' in request.FILES:
            update_kwargs['images'] = request.FILES.getlist('images')

        try:
            updated = ProductService.update_seller_product(
                seller_product=seller_product,
                **update_kwargs
            )
            response_serializer = SellerProductSerializer(updated)
            return success_response(
                data=response_serializer.data,
                http_status_code=status.HTTP_200_OK
            )
        except ValueError as e:
            return error_response(
                message=str(e),
                res_status="VALIDATION_ERROR",
                http_status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error updating seller product: {str(e)}")
            return error_response(
                message="Error updating product",
                res_status="ERROR",
                http_status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_summary="Delete or de-list seller product",
        responses={
            200: openapi.Response(description="Seller product de-listed"),
            401: openapi.Response(
                description="Unauthorized",
                schema=_error_response_schema
            ),
            404: openapi.Response(
                description="Not found",
                schema=_error_response_schema
            ),
        },
        tags=['Seller Portal']
    )
    def delete(self, request, seller_product_id):
        """Soft delete/de-list a seller product."""
        seller_product, error = self._get_seller_product(
            request=request,
            seller_product_id=seller_product_id
        )
        if error:
            return error

        try:
            ProductService.de_list_seller_product(seller_product)
            return success_response(
                data={'message': 'Seller product de-listed successfully'},
                http_status_code=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Error deleting seller product: {str(e)}")
            return error_response(
                message="Error deleting product",
                res_status="ERROR",
                http_status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
