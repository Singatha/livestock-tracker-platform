from django.contrib import admin

from .models import Feed, FeedingPlan, FeedingPlanItem

admin.site.register([Feed, FeedingPlan, FeedingPlanItem])
