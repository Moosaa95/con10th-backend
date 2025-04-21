from django.urls import path
from .endpoints import (
     CreateClientServiceRequest,
     CreateService,
     FetchServices,
     MarkExpertCompleted,
     AutoConfirmService,
     FetchClientServiceRequestSummary
     
     
)

urlpatterns = [
    # ###### SERVICES

    path('create_service', CreateService.as_view(), name='create-service'),
    
    path('fetch_client_service_request_summary', FetchClientServiceRequestSummary.as_view(), name='fetch-client-service-request-summary'),
    path('fetch_services', FetchServices.as_view(), name='fetch-services'),
    path('create_client_service_request', CreateClientServiceRequest.as_view(), name='create-service-request'),
    path('mark_completed', MarkExpertCompleted.as_view(), name='mark-service-completed'),
    path('auto_confirm', AutoConfirmService.as_view(), name='auto-confirm-service'),
]
