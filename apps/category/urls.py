from django.urls import path, include



urlpatterns = [
    path('', include('category.endpoints.categories.urls')),
    path('skill/', include('category.endpoints.skills.urls')),
]