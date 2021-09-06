from rest_framework import permissions


class IsConsumer(permissions.BasePermission):
    message = "User is not Consumer!"

    def has_permission(self, request, view):
        return request.user.atype == "C"


class IsVendor(permissions.BasePermission):
    message = "User is not Vendor!"

    def has_permission(self, request, view):
        return request.user.atype == "V"
