from django.db import models

# Create your models here.
class Conversation(models.Model):
    client = models.ForeignKey("CustomUser", on_delete=models.CASCADE, related_name='client_conversations')
    expert = models.ForeignKey("CustomUser", on_delete=models.CASCADE, related_name='expert_conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    expert_accepted = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('client', 'expert')
    
    def __str__(self):
        return f"Conversation between {self.client.username} and {self.expert.username}"
    
    # @classmethod
    # def get_last_message(cls, obj):
    #     last_message = obj.messages.order_by('-created_at').first()
    #     if last_message:
    #         return MessageSerializer(last_message).data
    #     return None
    
    # def get_unread_count(self, obj):
    #     user = self.context['request'].user
    #     return obj.messages.filter(is_read=False).exclude(sender=user).count()

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey("CustomUser", on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Message from {self.sender.username} at {self.timestamp}"


# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from core.models import BaseModel
# from apps.accounts.models import User


# class Conversation(BaseModel):
#     """Model for conversations between clients and experts."""
    
#     client = models.ForeignKey(
#         User, on_delete=models.CASCADE, 
#         related_name='client_conversations',
#         limit_choices_to={'user_type': 'client'}
#     )
#     expert = models.ForeignKey(
#         User, on_delete=models.CASCADE, 
#         related_name='expert_conversations',
#         limit_choices_to={'user_type': 'expert'}
#     )
#     is_accepted = models.BooleanField(_('is accepted'), default=False)
    
#     class Meta:
#         verbose_name = _('conversation')
#         verbose_name_plural = _('conversations')
#         unique_together = ('client', 'expert')
    
#     def __str__(self):
#         return f"Conversation: {self.client.email} - {self.expert.email}"


# class Message(BaseModel):
#     """Model for messages within a conversation."""
    
#     conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
#     sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
#     content = models.TextField(_('content'))
#     is_read = models.BooleanField(_('is read'), default=False)
    
#     class Meta:
#         verbose_name = _('message')
#         verbose_name_plural = _('messages')
#         ordering = ['created_at']
    
#     def __str__(self):
#         return f"Message from {self.sender.email} at {self.created_at}"
    
#     def save(self, *args, **kwargs):
#         """Override save to validate sender is part of the conversation."""
#         if self.sender != self.conversation.client and self.sender != self.conversation.expert:
#             raise ValueError("Sender must be part of the conversation")
        
#         # Check if this is the first message from client and conversation is not accepted
#         if (self.sender == self.conversation.client and 
#             not self.conversation.is_accepted and 
#             self.conversation.messages.filter(sender=self.conversation.client).exists()):
#             raise ValueError("Cannot send more messages until expert accepts the conversation")
        
#         super().save(*args, **kwargs)
