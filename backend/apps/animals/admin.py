from django.contrib import admin

from .models import Animal, Flock

admin.site.register(Flock)
admin.site.register(Animal)
