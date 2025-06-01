from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'reservations'

router = DefaultRouter()
router.register(r'', views.ReservationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('my-reservations/', views.ReservationViewSet.as_view({'get': 'my_reservations'}), name='my-reservations'),
    path('active/', views.ReservationViewSet.as_view({'get': 'active'}), name='active-reservations'),
] 