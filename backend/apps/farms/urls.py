from django.urls import path
from rest_framework.routers import SimpleRouter

from .team_views import (
    AcceptInvitationView,
    TeamAuditView,
    TeamInvitationDetailView,
    TeamInvitationsView,
    TeamMemberDetailView,
    TeamMembersView,
)
from .views import FarmViewSet

router = SimpleRouter()
router.register("", FarmViewSet, basename="farm")
urlpatterns = [
    path("team/members/", TeamMembersView.as_view(), name="team-members"),
    path(
        "team/members/<uuid:membership_id>/",
        TeamMemberDetailView.as_view(),
        name="team-member-detail",
    ),
    path("team/invitations/", TeamInvitationsView.as_view(), name="team-invitations"),
    path(
        "team/invitations/<uuid:invitation_id>/",
        TeamInvitationDetailView.as_view(),
        name="team-invitation-detail",
    ),
    path("team/audit/", TeamAuditView.as_view(), name="team-audit"),
    path("invitations/accept/", AcceptInvitationView.as_view(), name="invitation-accept"),
    *router.urls,
]
