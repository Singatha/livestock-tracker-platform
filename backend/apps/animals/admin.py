from django.contrib import admin

from .models import Animal, AnimalLifecycleEvent, Flock

admin.site.register(Flock)
admin.site.register(Animal)
admin.site.register(AnimalLifecycleEvent)
