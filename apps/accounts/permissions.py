# api/accounts/permissions.py
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return obj == request.user


class IsConversationParticipant(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to view or edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Check if user is part of the conversation
        if hasattr(obj, 'conversation'):  # For messages
            return request.user == obj.conversation.client or request.user == obj.conversation.expert
        return request.user == obj.client or request.user == obj.expert


class IsProjectParticipant(permissions.BasePermission):
    """
    Custom permission to only allow participants of a project to view or edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Check if user is part of the project
        return request.user == obj.client or request.user == obj.expert


class IsPaymentParticipant(permissions.BasePermission):
    """
    Custom permission to only allow participants of a payment to view it.
    """
    def has_object_permission(self, request, view, obj):
        # Check if user is part of the payment's project
        return request.user == obj.project.client or request.user == obj.project.expert