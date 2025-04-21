
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from accounts.models import ExpertUserProfile
from accounts.serializers import  (
    ExpertDetailRequestSerializer,
    ExpertFilterRequestSerializer,
    ExpertFilterSerializer,
    ExpertProfileSetupResponseSerializer,
    ExpertResultSerializer,
    ExpertUserProfileSerializer, 
    UploadExpertProfilePhotoSerializer, 
)
from django.db.models import Q


# EXPERTS
class GetExpertProfile(APIView):
    

    def post(self, request):
        data = dict(status=False, message="can get user")
        serializer = ExpertDetailRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        expert_detail = ExpertUserProfile.get_expert_profile(**validated_data, obj=True)
        if expert_detail:
            data.update(status=True, message="User Found")
        serializer = ExpertProfileSetupResponseSerializer(expert_detail)
        return Response(serializer.data)


class UpdateExpertProfile(APIView):
    
    
    def post(self, request):
        """Update expert profile details."""
        response_data = dict(status=False)
        serializer = ExpertUserProfileSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        expert_id = validated_data.get("expert_id")
        updated_profile = ExpertUserProfile.update_profile(expert_id, **serializer.validated_data)
        if not updated_profile:
            response_data.update(message="can not update")
            return Response(data=response_data, status=status.HTTP_404_NOT_FOUND)

        response_data.update(status=True)
        return Response(data=response_data, status=status.HTTP_200_OK)
            

class UploadExpertProfilePhoto(APIView):
    """API view for profile photo operations."""
    
    def post(self, request):
        response_data = dict(status=False, message="can not upload")
        serializer = UploadExpertProfilePhotoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        expert_id = serializer.validated_data.get("expert_id")
        profile_picture = serializer.validated_data.get("profile_picture")
        profile = ExpertUserProfile.update_photo(expert_id, profile_picture)
        if profile:
            response_data.update(status=True, message="image uploaded successfully")
                
        return Response(data=response_data, status=status.HTTP_200_OK)
        
    
class TopExpertsAPIView(APIView):
    """
    API endpoint to get top experts sorted by rating, completed jobs, earnings, or reviews.
    """
    permission_classes = [AllowAny]
    def post(self, request):
        limit = request.data.get('limit', 10)  # Default to top 10 experts
        order_by_field = request.data.get('order_by', 'rating')  # Default sort by rating

        try:
            top_experts = ExpertUserProfile.top_experts(limit=int(limit), order_by_field=order_by_field)
            serializer = ""
            return Response(data=top_experts, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        


class FetchExpertFilter(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        filters = request.data.get("filters", {})
        serializer = ExpertFilterSerializer(data=filters)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        # expert_id = serializer.validated_data.get("expert_id")
        count = serializer.validated_data.pop("count", 500)

        query = Q(is_profile_complete=True) & Q(has_agreed_to_terms=True)
        
        for key, value in validated_data.items():
            # if key == "skills":
            #     query &= Q(skills__in=value)  # Match any skill
            # elif key == "category":
            #     query &= Q(skills__category=value)
            # else:
            query &= Q(**{key: value})

        experts = ExpertUserProfile.fetch_experts(conditions=query, count=count)
        print("EXPERTS", dir(experts))
        serialized_data = ExpertResultSerializer(experts, many=True).data
        return Response(
            data=dict(status=True, message="Experts retrieved successfully", data=serialized_data),
            status=status.HTTP_200_OK,
        )
# TODO: registration should show already exist email in the frontend