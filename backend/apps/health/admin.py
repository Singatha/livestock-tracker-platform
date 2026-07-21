from django.contrib import admin

from .models import HealthObservation, Treatment

admin.site.register(HealthObservation)
admin.site.register(Treatment)
