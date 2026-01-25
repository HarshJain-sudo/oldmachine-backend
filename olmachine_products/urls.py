"""
URL configuration for olmachine_products app.
"""

from django.urls import path
from olmachine_products.views import (
    CategoriesDetailsView,
    CategoryProductsDetailsView,
    ProductDetailsView
)

app_name = 'olmachine_products'

urlpatterns = [
    path(
        'categories_details/get/v1/',
        CategoriesDetailsView.as_view(),
        name='categories_details'
    ),
    path(
        'category_products_details/get/v1/',
        CategoryProductsDetailsView.as_view(),
        name='category_products_details'
    ),
    path(
        'product_details/get/v1/<str:product_code>/',
        ProductDetailsView.as_view(),
        name='product_details'
    ),
]

