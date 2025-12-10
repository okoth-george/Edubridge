from rest_framework.permissions import BasePermission
from rest_framework import permissions

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'student'

class IsSponsor(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'sponsor'

class IsSponsorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow the sponsor (owner) of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the sponsor of the scholarship.
        return obj.sponsor == request.user