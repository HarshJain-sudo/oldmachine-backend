"""
URL configuration for olmachine_seller_portal app.
"""

from django.urls import path
from olmachine_seller_portal.views import (
    RootCategoriesView,
    CategoryChildrenView,
    FormConfigView,
    SellerProductListCreateView,
    SellerProductDetailView,
)

app_name = 'olmachine_seller_portal'

urlpatterns = [
    path(
        'categories/roots/',
        RootCategoriesView.as_view(),
        name='category_roots'
    ),
    path(
        'categories/children/<str:category_code>/',
        CategoryChildrenView.as_view(),
        name='category_children'
    ),
    path(
        'form/<str:category_code>/',
        FormConfigView.as_view(),
        name='form_config'
    ),
    path(
        'products/',
        SellerProductListCreateView.as_view(),
        name='seller_product_list_create'
    ),
    path(
        'products/<uuid:seller_product_id>/',
        SellerProductDetailView.as_view(),
        name='seller_product_detail'
    ),
]

