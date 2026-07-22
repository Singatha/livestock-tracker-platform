from django.urls import path

from .views import (
    ImportCommitView,
    ImportErrorsView,
    ImportJobsView,
    ImportPreviewView,
    ImportTemplateView,
)

urlpatterns = [
    path("", ImportJobsView.as_view(), name="import-jobs"),
    path("preview/", ImportPreviewView.as_view(), name="import-preview"),
    path("<uuid:job_id>/commit/", ImportCommitView.as_view(), name="import-commit"),
    path("<uuid:job_id>/errors/", ImportErrorsView.as_view(), name="import-errors"),
    path("templates/<str:kind>/", ImportTemplateView.as_view(), name="import-template"),
]
