from commons.validators import validate_amount
from rest_framework import serializers

class ServiceSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    # expert_id = serializers.UUIDField()
    skill_id = serializers.UUIDField()
    title = serializers.CharField()
    description = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2, validators=[validate_amount])
    # is_active = serializers.BooleanField(default=False, required=False)


class ServiceRequestSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    client_id = serializers.UUIDField()
    expert_id = serializers.UUIDField()
    service_id = serializers.UUIDField()
    service_title = serializers.CharField()  
    expert_name = serializers.CharField()  
    service_description = serializers.CharField()
    agreed_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    end_date = serializers.DateField()
    status = serializers.CharField()
    created_at = serializers.DateTimeField()

    def validate_agreed_price(self, value):
        """Ensure the agreed price is valid."""
        if value <= 0:
            raise serializers.ValidationError("Agreed price must be positive.")
        return value