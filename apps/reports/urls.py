from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReportViewSet

router = DefaultRouter()
router.register(r'reports', ReportViewSet, basename='report')

urlpatterns = [
    path('', include(router.urls)),
    path('reports/summary/', ReportViewSet.as_view({'get': 'summary'})),
    path('reports/monthly/', ReportViewSet.as_view({'get': 'monthly'})),
    path('reports/date-range/', ReportViewSet.as_view({'get': 'date_range'})),
    path('reports/parking-lot/<int:pk>/', ReportViewSet.as_view({'get': 'parking_lot'})),
    path('reports/export/', ReportViewSet.as_view({'get': 'export'})),
] 