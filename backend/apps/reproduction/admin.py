from django.contrib import admin

from .models import BirthRecord, BreedingRecord

admin.site.register(BreedingRecord)
admin.site.register(BirthRecord)
