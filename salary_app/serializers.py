from rest_framework import serializers

from salary_app.models import Employee


class EmployeeSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = [
            "id",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "job_title",
            "department",
            "country",
            "salary",
            "hire_date",
            "role",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["full_name", "created_at", "updated_at"]

    def get_full_name(self, obj):
        return obj.full_name