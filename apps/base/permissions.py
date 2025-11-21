from rest_framework.permissions import BasePermission

from apps.users.enums import UserRoleEnum


class IsAdminPermission(BasePermission):
    message = 'Permission denied, you are not the admin'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)

class IsAdminOrOwner(BasePermission):
    message = 'Permission denied.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if getattr(request.user, "role", None) == UserRoleEnum.ADMIN.value:
            return True

        if hasattr(obj, "user"):
            return obj.user == request.user
        if hasattr(obj, "owner"):
            return obj.owner == request.user
        if hasattr(obj, "wallet"):
            return obj.wallet.owner == request.user
        return False