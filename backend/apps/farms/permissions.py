from rest_framework.exceptions import NotFound
from rest_framework.permissions import SAFE_METHODS, BasePermission

from .models import Farm, FarmMembership


def selected_farm(request) -> Farm:
    farm_id = request.headers.get("X-Farm-ID")
    if not farm_id:
        raise NotFound("Select a farm using the X-Farm-ID header")
    try:
        return Farm.objects.get(
            id=farm_id, memberships__user=request.user, memberships__is_active=True
        )
    except (Farm.DoesNotExist, ValueError) as error:
        raise NotFound("Farm not found") from error


class FarmRecordPermission(BasePermission):
    def has_permission(self, request, view) -> bool:
        farm = selected_farm(request)
        request.selected_farm = farm
        if request.method in SAFE_METHODS:
            return True
        return FarmMembership.objects.filter(
            farm=farm,
            user=request.user,
            is_active=True,
            role__in=[
                FarmMembership.Role.OWNER,
                FarmMembership.Role.MANAGER,
                FarmMembership.Role.WORKER,
            ],
        ).exists()


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
