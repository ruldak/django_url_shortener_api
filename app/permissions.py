from rest_framework import permissions
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework_api_key.permissions import HasAPIKey

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.created_by == request.user

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user

class HasAPIKeyOrIsAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        if permissions.IsAuthenticated().has_permission(request, view):
            return True
        if HasAPIKey().has_permission(request, view):
            return True
        return False