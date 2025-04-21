from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiExample

from apps.category.models import  Skill
from apps.category.serializers import SkillSerializer


class CreateSkill(APIView):
    """
    POST: Create a new skill.
    """
    @extend_schema(
        tags=["Category"],
        description="Create a new skill. Users can request new skills that are not pre-defined.",
        request=SkillSerializer,
        responses={201: None},
        examples=[
            OpenApiExample(
                "Request Example",
                value={
                    "name": "Python Programming",
                    "status": "pending",
                    "is_predefined": False,
                    "category": None
                },
                request_only=True,
            ),
            OpenApiExample(
                "Response Example",
                value={
                    "status": True,
                    "message": "Skill created successfully"
                },
                response_only=True,
            ),
        ],
    )
    def post(self, request):
        response_data = dict(status=False)
        serializer = SkillSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)  
        skill = Skill.create_skill(**serializer.validated_data)
        if skill:
            response_data.update(status=True, message="Skill created successfully")
        return Response(data=response_data, status=status.HTTP_201_CREATED)


class SkillUpdate(APIView):
    """
    POST: Update a skill.
    """
    def post(self, request):
        response_data = dict(status=False)
        skill_id = request.data.get("skill_id")
        if not skill_id:
            response_data.update(error="Missing skill_id in request body")
            return Response(data=response_data, status=status.HTTP_400_BAD_REQUEST)

        serializer = SkillSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = Skill.update_skill(skill_id, **serializer.validated_data)
        
        if not updated:
            response_data.update(error="Skill not found")
            return Response(data=response_data, status=status.HTTP_404_NOT_FOUND)
    
        response_data.update(status=True, message="Skill updated successfully")
        return Response(data=response_data, status=status.HTTP_200_OK)


class SkillDelete(APIView):
    """
    POST: Delete a skill.
    """
    def post(self, request):
        response_data = dict(status=False)
        skill_id = request.data.get("skill_id")
        if not skill_id:
            response_data.update(error="Missing skill id in request body")
            return Response(data=response_data, status=status.HTTP_400_BAD_REQUEST)

        deleted = Skill.delete_skill(skill_id)
        if not deleted:
            return Response(data=response_data, status=status.HTTP_404_NOT_FOUND)
        
        response_data.update(status=True, message="Skill deleted successfully")
        return Response(data=response_data, status=status.HTTP_200_OK)
        

# class PopularSkills(APIView):
#     """
#     POST: Retrieve the most popular skills based on the number of experts.
#     """
#     def post(self, request):
#         limit = request.data.get("limit", 10)  # ✅ Default limit is 10 if not provided
#         skills = Skill.most_popular_skills(limit=limit)
#         return Response(skills, status=status.HTTP_200_OK)


class FetchSkills(APIView):
    """
    POST: Retrieve a list of all skills.
    """
    permission_classes = [AllowAny]  # Anyone can register
    def post(self, request):
        skills = Skill.list_all_skills()
        print("SKILLS", skills)
        return Response(data={"status":True, "data":skills}, status=status.HTTP_200_OK)
