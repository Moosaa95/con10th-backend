from commons.functions import clean_amount
from rest_framework import serializers

def validate_amount(value):
    try:
        return clean_amount(value)
    except ValueError:
        raise serializers.ValidationError("Invalid amount")
