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
from olmachine_seller_portal.models import CategoryFormConfig, SellerProfile
from olmachine_seller_portal.models import MAX_CATEGORY_DEPTH
from olmachine_seller_portal.serializers import (
    CategoryFormConfigSerializer,
    SellerProductSerializer,
    SellerProductCreateSerializer,
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


class SellerProductCreateView(APIView):
    """
    Create seller product (submit form).
    Only API for product creation. No list/detail/update/delete in seller portal.

    POST /api/seller-portal/products/
    """

    permission_classes = [IsAuthenticated, IsSeller]

    @swagger_auto_schema(
        operation_summary="Create seller product",
        operation_description=(
            "Create a new product. Provide category_code, name, and optional "
            "description, price, currency, tag, availability, extra_info (JSON), "
            "location, and images."
        ),
        request_body=SellerProductCreateSerializer,
        responses={
            201: openapi.Response(
                description="Product created successfully",
                schema=_create_product_response_schema
            ),
            400: openapi.Response(description="Bad request", schema=_error_response_schema),
            401: openapi.Response(description="Unauthorized", schema=_error_response_schema),
            404: openapi.Response(description="Seller profile not found", schema=_error_response_schema),
            500: openapi.Response(description="Server error", schema=_error_response_schema),
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
