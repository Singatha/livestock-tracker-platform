from django.contrib import admin

from .models import Farm, FarmInvitation, FarmMembership, FarmMembershipAudit

admin.site.register(Farm)
admin.site.register(FarmMembership)
admin.site.register(FarmInvitation)
admin.site.register(FarmMembershipAudit)
