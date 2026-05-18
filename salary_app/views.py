from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from salary_app.models import Employee, Role
from salary_app.permissions import EmployeeAccessPermission, is_privileged
from salary_app.serializers import EmployeeSerializer


class EmployeeViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeSerializer
    permission_classes = [EmployeeAccessPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["country", "department", "job_title", "role"]
    search_fields = ["first_name", "last_name", "email", "job_title"]
    ordering_fields = ["last_name", "salary", "hire_date", "created_at"]

    def get_queryset(self):
        user = self.request.user

        if is_privileged(user):
            return Employee.objects.filter(is_active=True)

        profile = getattr(user, "employee_profile", None)
        if profile:
            return Employee.objects.filter(pk=profile.pk, is_active=True)

        return Employee.objects.none()

    def destroy(self, request, *args, **kwargs):
        employee = self.get_object()
        employee.is_active = False
        employee.save()
        return Response(status=status.HTTP_204_NO_CONTENT)