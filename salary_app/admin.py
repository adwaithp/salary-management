#admin.py
from django.contrib import admin
from salary_app.models import Employee
# Register your models here.

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display  = ["full_name", "email", "job_title", "department", "country", "salary", "is_active"]
    list_filter   = ["department", "country", "is_active"]
    search_fields = ["first_name", "last_name", "email", "job_title"]
    ordering      = ["last_name", "first_name"]