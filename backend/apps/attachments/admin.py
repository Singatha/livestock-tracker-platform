from django.contrib import admin

from .models import Attachment


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ("title", "farm", "animal", "category", "original_filename", "created_at")
    list_filter = ("category",)
    search_fields = ("title", "original_filename", "animal__ear_tag")
