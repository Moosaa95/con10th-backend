from django.urls import path

from apps.category.endpoints.skills.endpoints import (
    CreateSkill,
    FetchSkills
    
)


urlpatterns = [
    path('create_skill', CreateSkill.as_view(), name='create_skill'),
    path('fetch_skills', FetchSkills.as_view(), name='fetch_skills'),
    
]