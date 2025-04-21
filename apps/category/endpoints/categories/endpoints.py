from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiExample

from apps.category.models import  Category
from apps.category.serializers import CategorySerializer



class CreateCategory(APIView):
    """
    POST: Create a new category.
    """
    @extend_schema(
        tags=["Categories"],
        description="Create a new category. Users can request new categories that are not pre-defined.",
        request=CategorySerializer,
        responses={201: None},
        examples=[
            OpenApiExample(
                "Request Example",
                value={
                    "name": "Plumbing",
                    "image": None,
                    "status": "pending",
                    "is_predefined": False
                },
                request_only=True,
            ),
            OpenApiExample(
                "Response Example",
                value={
                    "status": True,
                    "message": "Category created successfully"
                },
                response_only=True,
            ),
        ],
    )
    def post(self, request):
        response_data = dict(status=False)
        serializer = CategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)  
        category = Category.create_category(**serializer.validated_data)
        if category:
            response_data.update(status=True, message="Category created successfully")
        return Response(data=response_data, status=status.HTTP_201_CREATED)
    

class CategoryUpdate(APIView):
    """
    POST: Update a category.
    """
    @extend_schema(
        tags=["Categories"],
        description="Update an existing category.",
        request=CategorySerializer,
        responses={200: None},
        examples=[
            OpenApiExample(
                "Request Example",
                value={
                    "category_id": 1,
                    "name": "Updated Category Name",
                    "status": "active"
                },
                request_only=True,
            ),
            OpenApiExample(
                "Response Example",
                value={
                    "status": True,
                    "message": "Category updated successfully"
                },
                response_only=True,
            ),
        ],
    )
    def post(self, request):
        response_data = dict(status=False)
        serializer = CategorySerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)  
        category_id = serializer.validated_data.pop("category_id")
        updated_category = Category.update_category(category_id, **serializer.validated_data)
        if updated_category:
            response_data.update(status=True, message="Category updated successfully")
        return Response(data=response_data, status=status.HTTP_200_OK)
    

class FetchCategories(APIView):
    """
    POST: Retrieve a list of categories with optional filters.
    """
    permission_classes = [AllowAny]
    @extend_schema(
        tags=["Categories"],
        description="Retrieve a list of categories with optional filters.",
        request=None,
        responses={200: None},
        examples=[
            OpenApiExample(
                "Response Example",
                value=[
                    {
                        "id": 1,
                        "name": "Plumbing",
                        "image": None,
                        "status": "active",
                        "is_predefined": True
                    },
                    {
                        "id": 2,
                        "name": "Electrical",
                        "image": None,
                        "status": "active",
                        "is_predefined": True
                    }
                ],
                response_only=True,
            ),
        ],
    )
    def post(self, request):
        # filters = request.data.get("filters", {})
        # and_condition = Q()

        # if "date" in filters:
        #     filters["created_at__date"] = filters.pop("date")

        # for key, value in filters.items():
        #     and_condition &= Q(**{key: value})

        categories = Category.list_categories()
        print("LIT CATEGORIES=======", categories)
        serializer = CategorySerializer(categories, many=True)
        return Response(data=(dict(data=serializer.data, status=True)), status=status.HTTP_200_OK)


class PopularCategories(APIView):
    """
    POST: Retrieve a list of popular categories.
    """
    permission_classes = [AllowAny]
    @extend_schema(
        tags=["Categories"],
        description="Retrieve a list of popular categories.",
        request=None,
        responses={200: None},
        examples=[
            OpenApiExample(
                "Response Example",
                value=[
                    {
                        "id": 1,
                        "name": "Plumbing",
                        "image": None,
                        "status": "active",
                        "is_predefined": True
                    },
                    {
                        "id": 2,
                        "name": "Electrical",
                        "image": None,
                        "status": "active",
                        "is_predefined": True
                    }
                ],
                response_only=True,
            ),
        ],
    )
    def post(self, request):
        limit = request.data.get('limit', 10)  # Default to top 10 categories
        categories = Category.most_popular_categories(limit=limit)
        print("CATEGORIES", categories)

        return Response(data=(dict(data=CategorySerializer(categories, many=True).data, status=True)), status=status.HTTP_200_OK)

        