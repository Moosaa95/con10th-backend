from clients.serializers import ClientSummaryInputSerializer, ClientSummaryOutputSerializer
from rest_framework import generics
from .models import  Service, ServiceRequest
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from rest_framework.permissions import AllowAny
from .serializers import ServiceRequestSerializer, ServiceSerializer
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse


class CreateService(APIView):
    """
    POST: Create a new service.
    """
    def post(self, request):
        serializer = ServiceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = Service.create_service(**serializer.validated_data)
        if service:
            return Response({"status": True, "message": "Service created successfully"}, status=status.HTTP_201_CREATED)

        return Response({"status": False, "error": "Failed to create service"}, status=status.HTTP_400_BAD_REQUEST)


class UpdateService(APIView):
    """
    POST: Update an existing service.
    """
    def post(self, request):
        service_id = request.data.get("service_id")
        if not service_id:
            return Response({"status": False, "error": "Missing service_id in request body"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ServiceSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        updated = Service.update_service(service_id, **serializer.validated_data)
        if updated:
            return Response({"status": True, "message": "Service updated successfully"}, status=status.HTTP_200_OK)

        return Response({"status": False, "error": "Service not found"}, status=status.HTTP_404_NOT_FOUND)


class GetService(APIView):
    """
    POST: Retrieve a specific service by ID.
    """
    def post(self, request):
        service_id = request.data.get("service_id")
        if not service_id:
            return Response({"status": False, "error": "Missing service_id in request body"}, status=status.HTTP_400_BAD_REQUEST)

        service = Service.get_service(service_id)
        if service:
            return Response(ServiceSerializer(service).data, status=status.HTTP_200_OK)

        return Response({"status": False, "error": "Service not found"}, status=status.HTTP_404_NOT_FOUND)


class FetchServices(APIView):
    """
    POST: Retrieve a list of services with optional filters.
    """
    def post(self, request):
        filters = request.data.get("filters", {})
        # serializer.is_valid(raise_exception=True)
        # validated_data = serializer.validated_data
        and_condition = Q()

        if "date" in filters:
            filters["created_at__date"] = filters.pop("date")

        for key, value in filters.items():
            and_condition.add(Q(**{key: value}), Q.AND)

        # accounts = Account.fetch_accounts(filters=and_condition, count=count) if count else Account.fetch_accounts(filters=and_condition)
        # serialized_accounts = AccountSerializer(accounts, many=True).data

        services = Service.fetch_services(filters=and_condition)
        return Response(ServiceSerializer(services, many=True).data, status=status.HTTP_200_OK)


class DeleteService(APIView):
    """
    POST: Delete a service by ID.
    """
    def post(self, request):
        service_id = request.data.get("service_id")
        if not service_id:
            return Response({"status": False, "error": "Missing service_id in request body"}, status=status.HTTP_400_BAD_REQUEST)

        deleted = Service.delete_service(service_id)
        if deleted:
            return Response({"status": True, "message": "Service deleted successfully"}, status=status.HTTP_200_OK)

        return Response({"status": False, "error": "Service not found"}, status=status.HTTP_404_NOT_FOUND)


class ToggleServiceStatus(APIView):
    """
    POST: Toggle a service's active status.
    """
    def post(self, request):
        service_id = request.data.get("service_id")
        if not service_id:
            return Response({"status": False, "error": "Missing service_id in request body"}, status=status.HTTP_400_BAD_REQUEST)

        new_status = Service.toggle_service_status(service_id)
        if new_status is not None:
            return Response({"status": True, "message": f"Service is now {'active' if new_status else 'inactive'}"}, status=status.HTTP_200_OK)

        return Response({"status": False, "error": "Service not found"}, status=status.HTTP_404_NOT_FOUND)
    

class CreateClientServiceRequest(APIView):
    """
    POST: Create a new service request.
    """
    def post(self, request):
        serializer = ServiceRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service_request = ServiceRequest.create_request(**serializer.validated_data)
        if service_request:
            return Response({"status": True, "message": "Service request created successfully"}, status=status.HTTP_201_CREATED)
        
        return Response({"status": False, "error": "Failed to create request or request already exists"}, status=status.HTTP_400_BAD_REQUEST)


class MarkExpertCompleted(APIView):
    """
    POST: Expert marks a service as completed.
    """
    def post(self, request):
        service_id = request.data.get("service_id")
        if not service_id:
            return Response({"status": False, "error": "Missing service_id"}, status=status.HTTP_400_BAD_REQUEST)

        success = ServiceRequest.mark_expert_completed(service_id)
        if success:
            return Response({"status": True, "message": "Service marked as completed, awaiting client confirmation"}, status=status.HTTP_200_OK)

        return Response({"status": False, "error": "Service request not found or invalid status"}, status=status.HTTP_400_BAD_REQUEST)


class ConfirmService(APIView):
    """
    POST: Client confirms service completion, triggering payment release.
    """
    def post(self, request):
        service_id = request.data.get("service_id")
        if not service_id:
            return Response({"status": False, "error": "Missing service_id"}, status=status.HTTP_400_BAD_REQUEST)

        service_request = ServiceRequest.objects.filter(id=service_id).first()
        if not service_request:
            return Response({"status": False, "error": "Service request not found"}, status=status.HTTP_404_NOT_FOUND)

        success = ServiceRequest.confirm_service(service_request)
        if success:
            return Response({"status": True, "message": "Service confirmed successfully"}, status=status.HTTP_200_OK)

        return Response({"status": False, "error": "Service request could not be confirmed"}, status=status.HTTP_400_BAD_REQUEST)


class AutoConfirmService(APIView):
    """
    POST: Manually triggers auto-confirmation of completed services.
    """
    def post(self, request):
        ServiceRequest.auto_confirm_services()
        return Response({"status": True, "message": "Auto-confirmation triggered"}, status=status.HTTP_200_OK)


class FetchClientServiceRequestSummary(APIView):
    permission_classes = [AllowAny]
    """
    POST: Retrieve a summary of the client profile.
    """
    @extend_schema(
    tags=["Clients"],
    description="""
    Retrieves a comprehensive summary of a client's service request profile, including statistics 
    and recent activity. This endpoint provides information about total amounts spent, number of 
    requests by status, and details of recent service requests.
    """,
    request=ClientSummaryInputSerializer,
    responses={
        200: OpenApiResponse(
            response=dict,
            description="Successfully retrieved client summary information",
            examples=[
                OpenApiExample(
                    "Success Response",
                    value={
                        "status": True,
                        "data": {
                            "summary": {
                                "client_id": "550e8400-e29b-41d4-a716-446655440000",
                                "total_spent": "1250.50",
                                "total_requests": 15,
                                "active_requests": 3,
                                "completed_requests": 10,
                                "pending_requests": 2
                            },
                            "recent_requests": [
                                {
                                    "id": "7f9e8d7c-6b5a-4f3e-9d2c-1b0a9c8d7e6f",
                                    "status": "COMPLETED",
                                    "agreed_price": "350.00",
                                    "created_at": "2025-04-18T14:30:22Z"
                                },
                                {
                                    "id": "6e5d4c3b-2a1b-0c9d-8e7f-6a5b4c3d2e1f",
                                    "status": "IN_PROGRESS",
                                    "agreed_price": "250.00",
                                    "created_at": "2025-04-15T09:45:12Z"
                                },
                                {
                                    "id": "5d4c3b2a-1f0e-9d8c-7b6a-5f4e3d2c1b0a",
                                    "status": "PENDING",
                                    "agreed_price": "175.50",
                                    "created_at": "2025-04-12T16:20:05Z"
                                }
                            ]
                        }
                    },
                    response_only=True,
                ),
            ]
        ),
        400: OpenApiResponse(
            response=dict,
            description="Client not found or invalid request data",
            examples=[
                OpenApiExample(
                    "Client Not Found",
                    value={
                        "status": False,
                        "message": "User Not Found"
                    },
                    response_only=True,
                ),
                OpenApiExample(
                    "Invalid Request Data",
                    value={
                        "client_id": ["This field is required."]
                    },
                    response_only=True,
                ),
            ]
        ),
    },
    examples=[
        OpenApiExample(
            "Request Example",
            value={
                "client_id": "550e8400-e29b-41d4-a716-446655440000"
            },
            request_only=True,
        ),
    ],
    )

    def post(self, request):
        response_data = dict(status=False)
        serializer = ClientSummaryInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        if "client_id" not in validated_data:
            return Response(data={"status": False, "message": "Client ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        client_summary = ServiceRequest.get_client_stats(filters=validated_data)
        if not client_summary:
            response_data.update(message="User Not Found")
        
        summary_serializer = ClientSummaryOutputSerializer(client_summary.get("summary"))
        recent_requests_serializer = client_summary.get("recent_requests")

        return Response(data=dict(status=True, data={
            "summary": summary_serializer.data,
            "recent_requests": recent_requests_serializer
        }), status=status.HTTP_200_OK)
