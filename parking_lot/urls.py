from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import re_path as url
app_name = 'parking_lot'


urlpatterns = [

                path('', views.parking, name='parking'),
                url(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),


              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
