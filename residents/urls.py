from django.urls import path
from . import views

app_name = 'residents'

urlpatterns = [
    path('', views.residents, name='residents'),
    path('sign/', views.resident_sign, name='resident_sign'),
    path('<int:residents_number>/', views.change, name='change'),
]