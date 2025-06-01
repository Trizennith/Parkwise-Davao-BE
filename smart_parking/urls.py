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
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # Authentication
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/', include('apps.jwt_blacklist.urls')),
    
    # Apps
    path('api/accounts/', include('apps.accounts.urls')),
    path('api/parking/', include('apps.parking_lots.urls')),
    path('api/reservations/', include('apps.reservations.urls')),
    path('api/reports/', include('apps.reports.urls')),
] 