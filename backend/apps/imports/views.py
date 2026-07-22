import csv
import json

from django.http import HttpResponse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.farms.permissions import FarmManagerOnlyPermission, selected_farm

from .models import ImportJob
from .serializers import ImportJobSerializer, ImportPreviewSerializer
from .services import commit_import, create_preview, template_csv


class ImportJobsView(APIView):
    permission_classes = [FarmManagerOnlyPermission]

    @extend_schema(responses=ImportJobSerializer(many=True))
    def get(self, request):
        farm = selected_farm(request)
        jobs = ImportJob.objects.filter(farm=farm)[:50]
        return Response(ImportJobSerializer(jobs, many=True).data)


class ImportPreviewView(APIView):
    permission_classes = [FarmManagerOnlyPermission]

    @extend_schema(request=ImportPreviewSerializer, responses=ImportJobSerializer)
    def post(self, request):
        farm = selected_farm(request)
        serializer = ImportPreviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        job = create_preview(
            farm=farm,
            user=request.user,
            upload=serializer.validated_data.pop("file"),
            **serializer.validated_data,
        )
        return Response(ImportJobSerializer(job).data, status=status.HTTP_201_CREATED)


class ImportCommitView(APIView):
    permission_classes = [FarmManagerOnlyPermission]

    @extend_schema(request=None, responses=ImportJobSerializer)
    def post(self, request, job_id):
        farm = selected_farm(request)
        job = ImportJob.objects.filter(farm=farm, id=job_id).first()
        if job is None:
            return Response({"detail": "Import job not found"}, status=status.HTTP_404_NOT_FOUND)
        try:
            job = commit_import(job=job, user=request.user)
        except Exception as error:
            if isinstance(error, ValidationError):
                raise
            raise ValidationError({"detail": f"Import failed: {error}"}) from error
        return Response(ImportJobSerializer(job).data)


class ImportTemplateView(APIView):
    permission_classes = [FarmManagerOnlyPermission]

    @extend_schema(responses={(200, "text/csv"): OpenApiTypes.BINARY})
    def get(self, request, kind):
        selected_farm(request)
        if kind not in ImportJob.Kind.values:
            return Response({"detail": "Unknown import type"}, status=status.HTTP_404_NOT_FOUND)
        response = HttpResponse(template_csv(kind), content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{kind}-template.csv"'
        return response


class ImportErrorsView(APIView):
    permission_classes = [FarmManagerOnlyPermission]

    @extend_schema(responses={(200, "text/csv"): OpenApiTypes.BINARY})
    def get(self, request, job_id):
        farm = selected_farm(request)
        job = ImportJob.objects.filter(farm=farm, id=job_id).first()
        if job is None:
            return Response({"detail": "Import job not found"}, status=status.HTTP_404_NOT_FOUND)
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{job.kind}-errors.csv"'
        writer = csv.writer(response)
        writer.writerow(["Row", "Errors"])
        writer.writerows((error["row"], json.dumps(error["errors"])) for error in job.errors)
        return response
