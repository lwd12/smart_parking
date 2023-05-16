from django.urls import path
from . import views

app_name = 'camera'

urlpatterns = [
    path('', views.camera, name='camera'),
]