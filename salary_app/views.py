from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView

from salary_app import services
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


class InsightsPermission(EmployeeAccessPermission):
    """Insights are HR / Admin / Manager only."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and is_privileged(request.user)


class BaseInsightView(APIView):
    permission_classes = [InsightsPermission]

    def get_base_queryset(self):
        return Employee.objects.filter(is_active=True)


class OrgOverviewView(BaseInsightView):
    def get(self, request):
        data = services.get_org_overview(self.get_base_queryset())
        return Response(data)


class CountrySummaryView(BaseInsightView):
    def get(self, request):
        data = list(services.get_country_salary_summary(self.get_base_queryset()))
        return Response(data)


class JobTitleSummaryView(BaseInsightView):
    def get(self, request):
        country = request.query_params.get("country")
        data = list(services.get_job_title_salary_by_country(self.get_base_queryset(), country=country))
        return Response(data)


class DepartmentSummaryView(BaseInsightView):
    def get(self, request):
        data = list(services.get_department_salary_summary(self.get_base_queryset()))
        return Response(data)


class TopEarnersView(BaseInsightView):
    def get(self, request):
        limit = int(request.query_params.get("limit", 10))
        queryset = services.get_top_earners(self.get_base_queryset(), n=limit)
        serializer = EmployeeSerializer(queryset, many=True)
        return Response(serializer.data)