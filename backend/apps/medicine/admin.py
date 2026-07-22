from django.contrib import admin

from .models import DoseAdministration, MedicineBatch, MedicineProduct, TreatmentCourse

admin.site.register(MedicineProduct)
admin.site.register(MedicineBatch)
admin.site.register(TreatmentCourse)
admin.site.register(DoseAdministration)
