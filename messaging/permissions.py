from rest_framework import permissions


class IsSenderOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True if request.user in (obj.recipient, obj.sender) else False

        return obj.sender == request.user
