from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'parking_lots'

router = DefaultRouter()
router.register(r'lots', views.ParkingLotViewSet)
router.register(r'spaces', views.ParkingSpaceViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('parking-lots/<int:pk>/available-slots/', views.ParkingLotViewSet.as_view({'get': 'available_slots'}), name='parking-lot-available-slots'),
    path('parking-lots/<int:pk>/occupancy-rate/', views.ParkingLotViewSet.as_view({'get': 'occupancy_rate'}), name='parking-lot-occupancy-rate'),
] 