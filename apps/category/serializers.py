from rest_framework import serializers
from category.enums import StatusChoices



class CategorySerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(max_length=255)
    image = serializers.ImageField(required=False, allow_null=True)
    status = serializers.ChoiceField(choices=StatusChoices.choices, default=StatusChoices.STATUS_PENDING)
    is_predefined = serializers.BooleanField(default=False)
    requested_by = serializers.UUIDField(read_only=True, required=False)
    created_at = serializers.DateTimeField(read_only=True)


class SkillSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(max_length=255)
    image = serializers.ImageField(required=False, allow_null=True)
    status = serializers.ChoiceField(choices=StatusChoices.choices, default=StatusChoices.STATUS_PENDING)
    is_predefined = serializers.BooleanField(default=False)
    requested_by = serializers.UUIDField(read_only=True, required=False)
    created_at = serializers.DateTimeField(read_only=True)
    category = serializers.UUIDField(required=False, allow_null=True)



