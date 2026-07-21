from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from .models import Farm
from .permissions import FarmObjectPermission
from .serializers import FarmSerializer


class FarmViewSet(ModelViewSet):
    queryset = Farm.objects.none()
    serializer_class = FarmSerializer
    permission_classes = [IsAuthenticated, FarmObjectPermission]

    def get_queryset(self):
        return (
            Farm.objects.filter(memberships__user=self.request.user, memberships__is_active=True)
            .prefetch_related("memberships")
            .distinct()
        )
