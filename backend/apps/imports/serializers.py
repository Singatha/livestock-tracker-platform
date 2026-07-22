from rest_framework import serializers

from .models import ImportJob


class ImportPreviewSerializer(serializers.Serializer):
    kind = serializers.ChoiceField(choices=ImportJob.Kind.choices)
    mode = serializers.ChoiceField(choices=ImportJob.Mode.choices)
    file = serializers.FileField()

    def validate_file(self, file):
        if file.size > 2 * 1024 * 1024:
            raise serializers.ValidationError("CSV files must be 2 MB or smaller")
        if not file.name.lower().endswith(".csv"):
            raise serializers.ValidationError("Upload a CSV file")
        return file


class ImportJobSerializer(serializers.ModelSerializer):
    valid_rows = serializers.SerializerMethodField()

    class Meta:
        model = ImportJob
        fields = [
            "id",
            "kind",
            "mode",
            "status",
            "original_filename",
            "rows_total",
            "rows_succeeded",
            "rows_failed",
            "valid_rows",
            "errors",
            "created_at",
            "completed_at",
        ]

    def get_valid_rows(self, obj) -> int:
        invalid = {error["row"] for error in obj.errors}
        return sum(1 for row in obj.rows if row["row"] not in invalid)
