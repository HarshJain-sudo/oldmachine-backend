"""
URL configuration for olmachine_seller_portal app.
"""

from django.urls import path
from olmachine_seller_portal.views import (
    CategoryFormConfigListView,
    CategoryFormConfigDetailView,
    CategoriesWithFormsView,
    SellerProductFormView,
    SellerProductListView,
    SellerProductDetailView
)

app_name = 'olmachine_seller_portal'

urlpatterns = [
    # Form Configuration APIs (Admin)
    path(
        'category-form-configs/',
        CategoryFormConfigListView.as_view(),
        name='category_form_config_list'
    ),
    path(
        'category-form-configs/<str:category_code>/',
        CategoryFormConfigDetailView.as_view(),
        name='category_form_config_detail'
    ),

    # Seller Product APIs
    path(
        'categories/with-forms/',
        CategoriesWithFormsView.as_view(),
        name='categories_with_forms'
    ),
    path(
        'form/<str:category_code>/',
        SellerProductFormView.as_view(),
        name='seller_product_form'
    ),
    path(
        'products/',
        SellerProductListView.as_view(),
        name='seller_product_list'
    ),
    path(
        'products/<uuid:product_id>/',
        SellerProductDetailView.as_view(),
        name='seller_product_detail'
    ),
]

