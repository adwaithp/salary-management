from django.contrib.auth.models import User
from rest_framework import serializers

from salary_app.models import Employee, Department


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


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    job_title = serializers.CharField(max_length=100)
    department = serializers.ChoiceField(choices=Department.choices)
    country = serializers.CharField(max_length=100)
    salary = serializers.DecimalField(max_digits=12, decimal_places=2)
    hire_date = serializers.DateField()

    def validate_email(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        if Employee.objects.filter(email=value).exists():
            raise serializers.ValidationError("An employee with this email already exists.")
        return value
