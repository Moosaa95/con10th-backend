from rest_framework import serializers
from clients.models import ClientProfile



class ClientProfileSetupResponseSerializer(serializers.Serializer):
    first_name = serializers.CharField(source="client.first_name")
    last_name = serializers.CharField(source="client.last_name")
    email = serializers.EmailField(source="client.email")
    role = serializers.EmailField(source="client.role")
    bio = serializers.CharField()
    address = serializers.CharField()
    profile_picture = serializers.ImageField()
    phone_number = serializers.CharField()
    gender = serializers.CharField(source="client.gender")
    completion_percentage = serializers.IntegerField()


class ClientRequestSerializer(serializers.Serializer):
    client_id = serializers.UUIDField()


class ClientProfileSerializer(serializers.Serializer):
    """Serializer for client profile with user details."""
    
    id = serializers.UUIDField(read_only=True)
    client_id = serializers.UUIDField(required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    gender = serializers.CharField(required=False)
    country = serializers.CharField(required=False)
    bio = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(read_only=True)
    address = serializers.CharField(required=False, allow_blank=True)
    date_of_birth = serializers.DateField(required=False)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    profile_picture = serializers.ImageField(required=False, allow_null=True)
    
    total_spent = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    has_agreed_to_terms = serializers.BooleanField(required=False)
    is_profile_complete = serializers.BooleanField(read_only=True)
    completion_percentage = serializers.IntegerField(read_only=True)

    
class ClientProfilePhotoSerializer(serializers.ModelSerializer):
    """Serializer for profile photo updates."""
    class Meta:
        model = ClientProfile
        fields = ['id', 'profile_picture', 'completion_percentage', 'is_profile_complete']
        read_only_fields = ['completion_percentage', 'is_profile_complete']


class UploadClientProfilePhotoSerializer(serializers.Serializer):
    client_id = serializers.UUIDField(required=True)
    profile_picture = serializers.ImageField(required=True)


class ClientSummaryInputSerializer(serializers.Serializer):
    client_id = serializers.UUIDField(required=True)


class ClientSummaryOutputSerializer(serializers.Serializer):
    total_requests = serializers.IntegerField()
    active_requests = serializers.IntegerField()
    total_spent = serializers.DecimalField(max_digits=12, decimal_places=2)