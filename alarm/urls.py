from django.urls import path
from . import views

app_name = 'alarm'

urlpatterns = [
    path('', views.alarm, name='alarm'),
    path('get/', views.GetData.as_view(), name='GetData')

]
