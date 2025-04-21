# api/messaging/serializers.py
from rest_framework import serializers
from .models import Conversation, Message
from apps.accounts.serializers import CustomUserSerializer

class MessageSerializer(serializers.ModelSerializer):
    sender = CustomUserSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'is_read', 'created_at']
        read_only_fields = ['sender', 'is_read']

class ConversationSerializer(serializers.ModelSerializer):
    client = CustomUserSerializer(read_only=True)
    expert = CustomUserSerializer(read_only=True)
    # last_message = serializers.SerializerMethodField()
    # unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ['id', 'client', 'expert', 'is_accepted', 'created_at', 
                  'updated_at', 'last_message', 'unread_count']
        read_only_fields = ['is_accepted']
    
    # def get_last_message(self, obj):
    #     last_message = obj.messages.order_by('-created_at').first()
    #     if last_message:
    #         return MessageSerializer(last_message).data
    #     return None
    
    # def get_unread_count(self, obj):
    #     user = self.context['request'].user
    #     return obj.messages.filter(is_read=False).exclude(sender=user).count()

class CreateConversationSerializer(serializers.Serializer):
    expert_id = serializers.UUIDField(required=True)

class CreateMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['content']