from django.urls import path
from .endpoints import (
    CreateCategory,
    FetchCategories,
    PopularCategories,
)

urlpatterns = [
    path('create_category', CreateCategory.as_view(), name='create_category'),
    path('fetch_categories', FetchCategories.as_view(), name='fetch_categories'),
    path('popular_categories', PopularCategories.as_view(), name='popular_categories'),
]