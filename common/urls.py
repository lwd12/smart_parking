from django.urls import path
from . import views

app_name = 'common'

urlpatterns = [
    path('', views.login_api, name='login'),
    path('login/', views.login_api),
    path('logout', views.logout, name='logout'),
    path('signup/', views.signup, name='signup'),
]
