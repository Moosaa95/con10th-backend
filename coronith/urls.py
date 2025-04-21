from django.contrib import admin
from django.urls import path, include
# from django.conf.urls.static import static
# from django.conf import settings
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
# from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('api/', include('djoser.urls')),
    path('api/', include('apps.accounts.urls')),
    path('api/services/', include('apps.services.urls')),
    path('api/category/', include('apps.category.urls')),
    path('api/client/', include('apps.clients.urls')),

]


# if settings.DEBUG:
#     urlpatterns += staticfiles_urlpatterns()
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


urlpatterns += [
    # YOUR PATTERNS
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    path('__debug__/', include('debug_toolbar.urls')),
    
]

admin.site.site_header = "Coronith Admin"
admin.site.site_title = "Coronith Admin Portal"
admin.site.index_title = "Welcome to Coronith  Portal"
