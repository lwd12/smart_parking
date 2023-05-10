from django.urls import path
from . import views

app_name = 'camera'

urlpatterns = [
    path('', views.home, name='home'),
    path("detectme/", views.detectme, name='detectme'),
]