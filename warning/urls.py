from django.urls import path, include
from . import views

app_name = 'warning'

urlpatterns = [
    path('', views.warnings, name='warning')  # '/' 에 해당되는 path
]
