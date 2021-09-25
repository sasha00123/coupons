from rest_framework import permissions


class IsConsumer(permissions.BasePermission):
    message = "User is not Consumer!"

    def has_permission(self, request, view):
        return request.user.atype == "C"


class IsVendor(permissions.BasePermission):
    message = "User is not Vendor!"

    def has_permission(self, request, view):
        return request.user.atype == "V"


class IsOwnerOrReadOnly(permissions.BasePermission):
    message = "Access denied"

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        # Creating is allowed too
        if request.method == "POST":
            return True
        return obj.get_owner() == request.user or request.user.is_superuser


class IsEmailVerifiedOrReadOnly(permissions.BasePermission):
    message = "Verify your email address first!"

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.atype == "V" and request.user.vendor.verified


class IsNotRestricted(permissions.BasePermission):
    message = "You have been restricted to publish!"

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.atype == "V" and not request.user.vendor.restricted


class IsAdminUserOrReadOnly(permissions.BasePermission):
    message = "You're not an admin"

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_superuser


class IsAdmin(permissions.BasePermission):
    message = "You're not an admin"

    def has_permission(self, request, view):
        return request.user.is_superuser
