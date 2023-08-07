from rest_framework.permissions import BasePermission


class IsModerator(BasePermission):
    def has_permission(self, request, view):
        if request.user.groups.filter(name='moderators').exists():
            print('I am moderator')
            return True
        return request.user.is_superuser


class IsNotModerator(BasePermission):
    def has_permission(self, request, view):
        if request.user.groups.filter(name='moderators').exists():
            print('I am not moderator')
            return False
        return request.user.is_superuser or request.user.is_authenticated


class IsOwner(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        print(view.get_object().owner)
        return request.user == view.get_object().owner


class IsOwnerOrModerator(BasePermission):
    def has_permission(self, request, view):
        if request.user.groups.filter(name='moderators').exists() or request.user == view.get_object().owner:
            return True
        return request.user.is_superuser
