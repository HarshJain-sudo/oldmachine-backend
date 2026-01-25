"""
URL configuration for oldmachine_backend project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/marketplace/', include('olmachine_users.urls')),
    path('api/marketplace/', include('olmachine_products.urls')),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
]

if settings.DEBUG:  # noqa: F405
    urlpatterns += static(
        settings.MEDIA_URL,  # noqa: F405
        document_root=settings.MEDIA_ROOT  # noqa: F405
    )

