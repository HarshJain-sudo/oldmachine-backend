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
from django.core.exceptions import ValidationError
from olmachine_products.models import Category
from olmachine_seller_portal.models import (
    CategoryFormConfig,
    SellerProduct,
    SellerProfile
)
from olmachine_seller_portal.serializers import (
    CategoryFormConfigSerializer,
    CategoryFormConfigCreateSerializer,
    SellerProductSerializer,
    SellerProductCreateSerializer,
    ProductApprovalSerializer
)
from olmachine_seller_portal.permissions import (
    IsSeller,
    IsAdminOrTeam
)
from olmachine_seller_portal.services.product_service import (
    ProductService
)
from olmachine_seller_portal.services.form_service import FormService
from oldmachine_backend.utils.response_utils import (
    success_response,
    error_response
)

logger = logging.getLogger(__name__)


class CategoryFormConfigListView(APIView):
    """
    List and create category form configurations.

    GET /api/seller-portal/category-form-configs/
    POST /api/seller-portal/category-form-configs/
    """

    permission_classes = [IsAuthenticated, IsAdminOrTeam]

    @swagger_auto_schema(
        operation_summary="List category form configurations",
        operation_description="Get all category form configurations",
        manual_parameters=[
            openapi.Parameter(
                'category_code',
                openapi.IN_QUERY,
                description="Filter by category code",
                type=openapi.TYPE_STRING,
                required=False
            ),
        ],
        responses={
            200: openapi.Response(
                description="List of form configurations"
            ),
            401: openapi.Response(description="Unauthorized"),
        },
        tags=['Form Configuration']
    )
    def get(self, request):
        """List all category form configurations."""
        category_code = request.query_params.get('category_code')

        queryset = CategoryFormConfig.objects.select_related(
            'category'
        ).prefetch_related('fields').all()

        if category_code:
            queryset = queryset.filter(
                category__category_code=category_code
            )

        serializer = CategoryFormConfigSerializer(queryset, many=True)
        return success_response(
            data={'form_configs': serializer.data},
            http_status_code=status.HTTP_200_OK
        )

    @swagger_auto_schema(
        operation_summary="Create category form configuration",
        operation_description="Create form configuration for a category",
        request_body=CategoryFormConfigCreateSerializer,
        responses={
            201: openapi.Response(
                description="Form configuration created"
            ),
            400: openapi.Response(description="Bad request"),
            401: openapi.Response(description="Unauthorized"),
        },
        tags=['Form Configuration']
    )
    def post(self, request):
        """Create category form configuration."""
        serializer = CategoryFormConfigCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return error_response(
                message="Invalid form configuration data",
                res_status="INVALID_DATA",
                http_status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            form_config = serializer.save()
            response_serializer = CategoryFormConfigSerializer(form_config)
            return success_response(
                data=response_serializer.data,
                http_status_code=status.HTTP_201_CREATED
            )
        except Exception as e:
            logger.error(f"Error creating form config: {str(e)}")
            return error_response(
                message="Error creating form configuration",
                res_status="ERROR",
                http_status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CategoryFormConfigDetailView(APIView):
    """
    Get, update, delete category form configuration.

    GET /api/seller-portal/category-form-configs/{category_code}/
    PUT /api/seller-portal/category-form-configs/{id}/
    DELETE /api/seller-portal/category-form-configs/{id}/
    """

    permission_classes = [IsAuthenticated, IsAdminOrTeam]

    @swagger_auto_schema(
        operation_summary="Get form configuration by category code",
        operation_description="Get form configuration for a category",
        responses={
            200: openapi.Response(
                description="Form configuration"
            ),
            404: openapi.Response(description="Not found"),
        },
        tags=['Form Configuration']
    )
    def get(self, request, category_code):
        """Get form configuration for a category."""
        try:
            category = Category.objects.get(
                category_code=category_code,
                is_active=True
            )
            form_config = get_object_or_404(
                CategoryFormConfig,
                category=category
            )
            serializer = CategoryFormConfigSerializer(form_config)
            return success_response(
                data=serializer.data,
                http_status_code=status.HTTP_200_OK
            )
        except Category.DoesNotExist:
            return error_response(
                message="Category not found",
                res_status="CATEGORY_NOT_FOUND",
                http_status_code=status.HTTP_404_NOT_FOUND
            )

    @swagger_auto_schema(
        operation_summary="Update form configuration",
        operation_description="Update form configuration for a category",
        request_body=CategoryFormConfigCreateSerializer,
        responses={
            200: openapi.Response(description="Form configuration updated"),
            400: openapi.Response(description="Bad request"),
            404: openapi.Response(description="Not found"),
        },
        tags=['Form Configuration']
    )
    def put(self, request, category_code):
        """Update form configuration."""
        try:
            category = Category.objects.get(
                category_code=category_code,
                is_active=True
            )
            form_config = get_object_or_404(
                CategoryFormConfig,
                category=category
            )
        except Category.DoesNotExist:
            return error_response(
                message="Category not found",
                res_status="CATEGORY_NOT_FOUND",
                http_status_code=status.HTTP_404_NOT_FOUND
            )

        serializer = CategoryFormConfigCreateSerializer(
            form_config,
            data=request.data
        )
        if not serializer.is_valid():
            return error_response(
                message="Invalid form configuration data",
                res_status="INVALID_DATA",
                http_status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            form_config = serializer.save()
            response_serializer = CategoryFormConfigSerializer(form_config)
            return success_response(
                data=response_serializer.data,
                http_status_code=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Error updating form config: {str(e)}")
            return error_response(
                message="Error updating form configuration",
                res_status="ERROR",
                http_status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_summary="Delete form configuration",
        operation_description="Delete form configuration for a category",
        responses={
            200: openapi.Response(description="Form configuration deleted"),
            404: openapi.Response(description="Not found"),
        },
        tags=['Form Configuration']
    )
    def delete(self, request, category_code):
        """Delete form configuration."""
        try:
            category = Category.objects.get(
                category_code=category_code,
                is_active=True
            )
            form_config = get_object_or_404(
                CategoryFormConfig,
                category=category
            )
        except Category.DoesNotExist:
            return error_response(
                message="Category not found",
                res_status="CATEGORY_NOT_FOUND",
                http_status_code=status.HTTP_404_NOT_FOUND
            )

        try:
            form_config.delete()
            return success_response(
                data={'message': 'Form configuration deleted successfully'},
                http_status_code=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Error deleting form config: {str(e)}")
            return error_response(
                message="Error deleting form configuration",
                res_status="ERROR",
                http_status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CategoriesWithFormsView(APIView):
    """
    List categories that have form configurations.

    GET /api/seller-portal/categories/with-forms/
    """

    permission_classes = [IsAuthenticated, IsSeller]

    @swagger_auto_schema(
        operation_summary="List categories with form configurations",
        operation_description=(
            "Get list of categories that have active form "
            "configurations for sellers"
        ),
        responses={
            200: openapi.Response(
                description="List of categories with forms"
            ),
            401: openapi.Response(description="Unauthorized"),
        },
        tags=['Seller Products']
    )
    def get(self, request):
        """List categories with form configurations."""
        categories = Category.objects.filter(
            is_active=True,
            form_config__is_active=True
        ).select_related('form_config').distinct()

        categories_data = []
        for category in categories:
            categories_data.append({
                'category_code': category.category_code,
                'category_name': category.name,
                'description': category.description,
                'image_url': category.image_url,
                'has_form': True
            })

        return success_response(
            data={'categories': categories_data},
            http_status_code=status.HTTP_200_OK
        )


class SellerProductFormView(APIView):
    """
    Get form configuration for seller to fill.

    GET /api/seller-portal/form/{category_code}/
    """

    permission_classes = [IsAuthenticated, IsSeller]

    @swagger_auto_schema(
        operation_summary="Get form for category",
        operation_description=(
            "Get form configuration with fields for seller to fill"
        ),
        responses={
            200: openapi.Response(
                description="Form configuration"
            ),
            404: openapi.Response(description="Not found"),
        },
        tags=['Seller Products']
    )
    def get(self, request, category_code):
        """Get form configuration for a category."""
        try:
            form_config = FormService.get_form_config(category_code)
            serializer = CategoryFormConfigSerializer(form_config)
            return success_response(
                data=serializer.data,
                http_status_code=status.HTTP_200_OK
            )
        except ValidationError as e:
            return error_response(
                message=str(e),
                res_status="FORM_CONFIG_NOT_FOUND",
                http_status_code=status.HTTP_404_NOT_FOUND
            )


class SellerProductListView(APIView):
    """
    List and create seller products.

    GET /api/seller-portal/products/
    POST /api/seller-portal/products/
    """

    permission_classes = [IsAuthenticated, IsSeller]

    @swagger_auto_schema(
        operation_summary="List seller products",
        operation_description="Get list of products created by seller",
        manual_parameters=[
            openapi.Parameter(
                'status',
                openapi.IN_QUERY,
                description="Filter by status",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'category_code',
                openapi.IN_QUERY,
                description="Filter by category code",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'limit',
                openapi.IN_QUERY,
                description="Number of results",
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'offset',
                openapi.IN_QUERY,
                description="Offset for pagination",
                type=openapi.TYPE_INTEGER,
                required=False
            ),
        ],
        responses={
            200: openapi.Response(
                description="List of seller products"
            ),
            401: openapi.Response(description="Unauthorized"),
        },
        tags=['Seller Products']
    )
    def get(self, request):
        """List seller's products."""
        # Get seller profile
        try:
            seller_profile = SellerProfile.objects.get(
                user=request.user
            )
            seller = seller_profile.seller
        except SellerProfile.DoesNotExist:
            return error_response(
                message="Seller profile not found",
                res_status="SELLER_PROFILE_NOT_FOUND",
                http_status_code=status.HTTP_404_NOT_FOUND
            )

        # Filter products
        queryset = SellerProduct.objects.filter(
            seller=seller
        ).select_related(
            'product',
            'product__category',
            'product__seller',
            'product__location'
        ).prefetch_related(
            'product__images',
            'product__specifications'
        )

        # Apply filters
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        category_code = request.query_params.get('category_code')
        if category_code:
            queryset = queryset.filter(
                product__category__category_code=category_code
            )

        # Pagination
        limit = int(request.query_params.get('limit', 10))
        offset = int(request.query_params.get('offset', 0))
        queryset = queryset[offset:offset + limit]

        serializer = SellerProductSerializer(queryset, many=True)
        return success_response(
            data={'products': serializer.data},
            http_status_code=status.HTTP_200_OK
        )

    @swagger_auto_schema(
        operation_summary="Create seller product",
        operation_description="Create a new product from form submission",
        request_body=SellerProductCreateSerializer,
        responses={
            201: openapi.Response(
                description="Product created successfully"
            ),
            400: openapi.Response(description="Bad request"),
            401: openapi.Response(description="Unauthorized"),
        },
        tags=['Seller Products']
    )
    def post(self, request):
        """Create seller product from form submission."""
        # Get seller profile
        try:
            seller_profile = SellerProfile.objects.get(
                user=request.user
            )
            seller = seller_profile.seller
        except SellerProfile.DoesNotExist:
            return error_response(
                message="Seller profile not found",
                res_status="SELLER_PROFILE_NOT_FOUND",
                http_status_code=status.HTTP_404_NOT_FOUND
            )

        # Validate input
        serializer = SellerProductCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message="Invalid product data",
                res_status="INVALID_DATA",
                http_status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Create product
            seller_product = ProductService.create_seller_product(
                seller=seller,
                category_code=serializer.validated_data['category_code'],
                form_data=serializer.validated_data['form_data'],
                images=request.FILES.getlist('images'),
                location_data=serializer.validated_data.get('location')
            )

            response_serializer = SellerProductSerializer(seller_product)
            return success_response(
                data=response_serializer.data,
                http_status_code=status.HTTP_201_CREATED
            )

        except ValidationError as e:
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
    Get, update, delete seller product.

    GET /api/seller-portal/products/{product_id}/
    PUT /api/seller-portal/products/{product_id}/
    DELETE /api/seller-portal/products/{product_id}/
    """

    permission_classes = [IsAuthenticated, IsSeller]

    def get_seller_product(self, product_id, user):
        """Get seller product and verify ownership."""
        try:
            seller_profile = SellerProfile.objects.get(user=user)
            seller = seller_profile.seller
            seller_product = get_object_or_404(
                SellerProduct,
                id=product_id,
                seller=seller
            )
            return seller_product
        except SellerProfile.DoesNotExist:
            return None

    @swagger_auto_schema(
        operation_summary="Get seller product details",
        operation_description="Get details of a seller product",
        responses={
            200: openapi.Response(description="Product details"),
            404: openapi.Response(description="Not found"),
        },
        tags=['Seller Products']
    )
    def get(self, request, product_id):
        """Get seller product details."""
        seller_product = self.get_seller_product(product_id, request.user)

        if not seller_product:
            return error_response(
                message="Product not found or access denied",
                res_status="PRODUCT_NOT_FOUND",
                http_status_code=status.HTTP_404_NOT_FOUND
            )

        serializer = SellerProductSerializer(seller_product)
        return success_response(
            data=serializer.data,
            http_status_code=status.HTTP_200_OK
        )

    @swagger_auto_schema(
        operation_summary="Update seller product",
        operation_description="Update a seller product",
        request_body=SellerProductCreateSerializer,
        responses={
            200: openapi.Response(description="Product updated"),
            400: openapi.Response(description="Bad request"),
            404: openapi.Response(description="Not found"),
        },
        tags=['Seller Products']
    )
    def put(self, request, product_id):
        """Update seller product."""
        seller_product = self.get_seller_product(product_id, request.user)

        if not seller_product:
            return error_response(
                message="Product not found or access denied",
                res_status="PRODUCT_NOT_FOUND",
                http_status_code=status.HTTP_404_NOT_FOUND
            )

        # Only allow update if status is draft or rejected
        if seller_product.status not in ['draft', 'rejected']:
            return error_response(
                message=(
                    "Product can only be updated when status is "
                    "draft or rejected"
                ),
                res_status="INVALID_STATUS",
                http_status_code=status.HTTP_400_BAD_REQUEST
            )

        # Validate input
        serializer = SellerProductCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message="Invalid product data",
                res_status="INVALID_DATA",
                http_status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Update product (simplified - in production, implement full update)
            # For now, return success
            return error_response(
                message="Update functionality to be implemented",
                res_status="NOT_IMPLEMENTED",
                http_status_code=status.HTTP_501_NOT_IMPLEMENTED
            )

        except Exception as e:
            logger.error(f"Error updating seller product: {str(e)}")
            return error_response(
                message="Error updating product",
                res_status="ERROR",
                http_status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_summary="Delete seller product",
        operation_description="Delete a seller product",
        responses={
            200: openapi.Response(description="Product deleted"),
            404: openapi.Response(description="Not found"),
        },
        tags=['Seller Products']
    )
    def delete(self, request, product_id):
        """Delete seller product."""
        seller_product = self.get_seller_product(product_id, request.user)

        if not seller_product:
            return error_response(
                message="Product not found or access denied",
                res_status="PRODUCT_NOT_FOUND",
                http_status_code=status.HTTP_404_NOT_FOUND
            )

        try:
            # Delete product (cascade will delete related data)
            seller_product.product.delete()
            return success_response(
                data={'message': 'Product deleted successfully'},
                http_status_code=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Error deleting seller product: {str(e)}")
            return error_response(
                message="Error deleting product",
                res_status="ERROR",
                http_status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
