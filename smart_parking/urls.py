from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

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
        path('login/', TokenObtainPairView.as_view()),
        path('refresh-token/', TokenRefreshView.as_view()),
        path('', include('apps.jwt_blacklist.urls')),
        path('', include('apps.accounts.urls')),
    ])),
    
    # User endpoints
    path('api/user/', include([
        path('', include('apps.reservations.urls')),
        path('', include('apps.parking_lots.urls')),
    ])),

    # Admin API endpoints (changed from admin-api to api/admin)
    path('api/admin/', include([
        path('', include('apps.accounts.urls')),
        path('', include('apps.parking_lots.urls')),
        path('', include('apps.reservations.urls')),
        path('', include('apps.reports.urls')),
    ])),
] 