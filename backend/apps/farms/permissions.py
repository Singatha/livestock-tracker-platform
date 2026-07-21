from rest_framework.permissions import SAFE_METHODS, BasePermission

from .models import FarmMembership


class FarmObjectPermission(BasePermission):
    def has_object_permission(self, request, view, farm) -> bool:
        membership = FarmMembership.objects.filter(
            farm=farm, user=request.user, is_active=True
        ).first()
        if membership is None:
            return False
        if request.method in SAFE_METHODS:
            return True
        return membership.role in {
            FarmMembership.Role.OWNER,
            FarmMembership.Role.MANAGER,
        }
