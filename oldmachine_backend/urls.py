"""
URL configuration for oldmachine_backend project.
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# Swagger/OpenAPI Schema View
schema_view = get_schema_view(
    openapi.Info(
        title="OldMachine Backend API",
        default_version='v1',
        description=(
            "API documentation for OldMachine Backend. "
            "This API provides endpoints for user authentication, "
            "product management, and category browsing with "
            "personalized recommendations."
        ),
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@oldmachine.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=[
        path('api/marketplace/', include('olmachine_users.urls')),
        path('api/marketplace/', include('olmachine_products.urls')),
    ],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/marketplace/', include('olmachine_users.urls')),
    path('api/marketplace/', include('olmachine_products.urls')),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    
    # Swagger/OpenAPI URLs
    re_path(
        r'^swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=0),
        name='schema-json'
    ),
    re_path(
        r'^swagger/$',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'
    ),
    re_path(
        r'^redoc/$',
        schema_view.with_ui('redoc', cache_timeout=0),
        name='schema-redoc'
    ),
    re_path(
        r'^api-docs/$',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='api-docs'
    ),
]

if settings.DEBUG:  # noqa: F405
    urlpatterns += static(
        settings.MEDIA_URL,  # noqa: F405
        document_root=settings.MEDIA_ROOT  # noqa: F405
    )

