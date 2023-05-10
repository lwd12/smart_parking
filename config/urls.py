# from django.contrib import admin
from django.urls import path, include
from pybo.views import base_views
from django.urls import re_path as url
from django.views.static import serve
from django.conf import settings

urlpatterns = [
    url(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
    # path('admin/', admin.site.urls),
    path('common/', include('common.urls')),
    path('pybo/', include('pybo.urls')),
    path('', include('common.urls')),  # '/' 에 해당되는 path
    path('camera/', include('camera.urls')),
    path('parking_lot/', include('parking_lot.urls')),
    path('logs/', include('log.urls')),
    path('visitor/', include('visitor.urls')),
    path('warning/', include('warning.urls')),
    path('residents/', include('residents.urls')),

]

handler404 = 'common.views.page_not_found'
