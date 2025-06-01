from django.urls import path
from . import views

app_name = 'jwt_blacklist'

urlpatterns = [
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('logout-all/', views.LogoutAllView.as_view(), name='logout-all'),
] 