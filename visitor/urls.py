from django.urls import path
from . import views

app_name = 'visitor'

urlpatterns = [
    path('', views.visitor, name='visitor'),
    path('delete/<int:visitor_information_number>/', views.delete, name='visitor_delete'),

]
