"""
URL configuration for olmachine_seller_portal app.
"""

from django.urls import path
from olmachine_seller_portal.views import (
    RootCategoriesView,
    CategoryChildrenView,
    FormConfigView,
    SellerProductCreateView,
)

app_name = 'olmachine_seller_portal'

# Only 4 APIs per requirement: roots -> children -> form config -> create product
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
        SellerProductCreateView.as_view(),
        name='seller_product_create'
    ),
]

