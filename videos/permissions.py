__author__ = 'leomaltrait'

from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

class IsMember(permissions.BasePermission):
    """
    Check if the user is a paid member of the service
    """
    def has_permission(self, request, view):
        #print(view.get_object().free_preview)
        if request.user.is_authenticated() or view.get_object().free_preview:
            try:
                is_member = request.user.is_member
            except:
                is_member = None
            if is_member or view.get_object().free_preview:
                return True
            else:
                raise PermissionDenied("You must be a member to watch this.")
        else:
            raise PermissionDenied("You must be logged in to watch this.")
