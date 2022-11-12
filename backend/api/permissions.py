from rest_framework import permissions


class CustomerAccessPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user and request.user.is_authenticated
