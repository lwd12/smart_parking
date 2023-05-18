from django.urls import path, include


urlpatterns = [
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
    path('alarm/', include('alarm.urls')),
]

handler404 = 'common.views.page_not_found'
