from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from clients.models import ClientProfile
from clients.serializers import (
    ClientProfilePhotoSerializer,
    ClientProfileSerializer, 
    ClientProfileSetupResponseSerializer, 
    ClientRequestSerializer,
    UploadClientProfilePhotoSerializer,
)
from drf_spectacular.utils import OpenApiExample, extend_schema



# CLIENT

class GetClientProfileView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print("request", request.data)
        data = dict(status=False, message="can get user")
        serializer = ClientRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        client_detail = ClientProfile.get_client_profile(**validated_data, obj=True)
        if client_detail:
            data.update(status=True, message="User Found")

        serializer = ClientProfileSetupResponseSerializer(client_detail)
        return Response(serializer.data)


class UpdateClientProfileView(APIView):
    
    
    def post(self, request):
        """Update client profile details."""
        response_data = dict(status=False)
        serializer = ClientProfileSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        client_id = validated_data.pop("client_id")
        updated_profile = ClientProfile.update_client_profile(client_id, **serializer.validated_data)
        result = ClientProfileSerializer(updated_profile)
        return Response(result.data)
            

class UploadClientProfilePhotoView(APIView):
    """API view for profile photo operations."""
    
    def post(self, request):
        serializer = UploadClientProfilePhotoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        client_id = serializer.validated_data.get("client_id")
        profile_picture = serializer.validated_data.get("profile_picture")
        profile = ClientProfile.update_photo(client_id, profile_picture)
            
        if not profile:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
                
        serializer = ClientProfilePhotoSerializer(profile)
        return Response(serializer.data)


# class FetchClientSummary(APIView):
#     permission_classes = [AllowAny]
#     """
#     POST: Retrieve a summary of the client profile.
#     """
#     @extend_schema(
#         tags=["Clients"],
#         description="Retrieve a summary of the client profile.",
#         request=None,
#         responses={200: None},
#         examples=[
#             OpenApiExample(
#                 "Response Example",
#                 value={
#                     "status": True,
#                     "message": "User Found",
#                     "client_summary": {
#                         "active_service_requests": 5,
#                         "all_service_requests": 10,
#                         "total_amount_spent": 1000,
#                     }
#                 },
#                 response_only=True,
#             ),
#             OpenApiExample(
#                 "Response Example",
#                 value={
#                     "status": False,
#                     "message": "User Not Found"
#                 },
#                 response_only=True,
#             ),
#         ],
#     )

#     def post(self, request):
#         response_data = dict(status=False)
#         serializer = ClientSummarySerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         validated_data = serializer.validated_data
#         client_summary = ClientProfile.get_client_stats(**validated_data)
#         if not client_summary:
#             response_data.update(status=False, message="User Not Found")
        
#         serializer = ClientSummarySerializer(client_summary)

#         return Response(data=dict(status=True, **serializer.data), status=status.HTTP_200_OK)


