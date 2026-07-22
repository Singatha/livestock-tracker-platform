from django.urls import path

from .views import ReportsActivityView, ReportsExportView, ReportsOverviewView

urlpatterns = [
    path("overview/", ReportsOverviewView.as_view(), name="reports-overview"),
    path("activity/", ReportsActivityView.as_view(), name="reports-activity"),
    path("export/<str:report_type>/", ReportsExportView.as_view(), name="reports-export"),
]
