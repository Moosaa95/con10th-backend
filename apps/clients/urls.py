from django.urls import path

from clients.endpoints import (
    GetClientProfileView,
    UpdateClientProfileView,
    UploadClientProfilePhotoView,
    # FetchClientSummary,
)

urlpatterns = [
    # path('fetch_client_summary', FetchClientSummary.as_view(), name='fetch_client_summary'),
    path("get_client", GetClientProfileView.as_view(), name="get_client"),
    path('update_client_profile', UpdateClientProfileView.as_view(), name='client-profile'),
    path('update_client_photo', UploadClientProfilePhotoView.as_view(), name='profile-photo'),
]