from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from app.api.realtime.routing import websocket_urlpatterns

schema_view = get_schema_view(
    openapi.Info(
        title="Smart Parking Davao API",
        default_version='v1',
        description="API documentation for Smart Parking Davao",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@smartparkingdavao.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),  # Django admin with trailing slash
    
    # API Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0)),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0)),
    
    # Authentication
    path('api/auth/', include([
        path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('refresh-token/', TokenRefreshView.as_view()),
        path('', include('app.api.jwt_blacklist.urls')),
        path('', include('app.api.accounts.urls')),
    ])),
    
    # User endpoints
    path('api/user/', include([
        path('', include('app.api.reservations.urls')),
        path('', include('app.api.parking_lots.urls')),
        path('', include('app.api.notification.urls')),
    ])),

    # Admin API endpoints (changed from admin-api to api/admin)
    path('api/admin/', include([
        path('', include('app.api.accounts.urls')),
        path('', include('app.api.parking_lots.urls')),
        path('', include('app.api.reservations.urls')),
        path('', include('app.api.reports.urls')),
    ])),
]

# Add WebSocket URL patterns
urlpatterns += websocket_urlpatterns

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 