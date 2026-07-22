from pathlib import Path

from django.http import FileResponse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from apps.farms.models import FarmMembership
from apps.farms.viewsets import FarmScopedModelViewSet

from .models import Attachment
from .serializers import AttachmentSerializer


class AttachmentViewSet(FarmScopedModelViewSet):
    queryset = Attachment.objects.none()
    serializer_class = AttachmentSerializer
    http_method_names = ["get", "post", "delete", "head", "options"]

    def get_queryset(self):
        queryset = Attachment.objects.filter(farm=self.farm).select_related("animal", "uploaded_by")
        if animal := self.request.query_params.get("animal"):
            queryset = queryset.filter(animal_id=animal)
        if category := self.request.query_params.get("category"):
            queryset = queryset.filter(category=category)
        return queryset

    def get_serializer_context(self):
        return {**super().get_serializer_context(), "farm": self.farm}

    def destroy(self, request, *args, **kwargs):
        attachment = self.get_object()
        membership = FarmMembership.objects.get(farm=self.farm, user=request.user, is_active=True)
        if attachment.uploaded_by_id != request.user.id and membership.role not in {
            FarmMembership.Role.OWNER,
            FarmMembership.Role.MANAGER,
        }:
            raise PermissionDenied("Only the uploader, farm owner, or manager can delete this file")
        stored_file = attachment.file
        attachment.delete()
        stored_file.delete(save=False)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(responses={(200, "application/octet-stream"): OpenApiTypes.BINARY})
    @action(detail=True, methods=["get"])
    def content(self, request, pk=None):
        attachment = self.get_object()
        disposition = "inline" if attachment.content_type.startswith("image/") else "attachment"
        filename = Path(attachment.original_filename).name.replace('"', "")
        response = FileResponse(
            attachment.file.open("rb"),
            content_type=attachment.content_type,
            as_attachment=disposition == "attachment",
            filename=filename,
        )
        response["X-Content-Type-Options"] = "nosniff"
        return response
