from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from salary_app import services
from salary_app.models import Employee
from salary_app.serializers import EmployeeSerializer


class EmployeeViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["country", "department", "job_title"]
    search_fields = ["first_name", "last_name", "email", "job_title"]
    ordering_fields = ["last_name", "salary", "hire_date", "created_at"]

    def get_queryset(self):
        return Employee.objects.filter(is_active=True)

    def destroy(self, request, *args, **kwargs):
        employee = self.get_object()
        employee.is_active = False
        employee.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BaseInsightView(APIView):
    permission_classes = [IsAuthenticated]

    def get_base_queryset(self):
        return Employee.objects.filter(is_active=True)


class OrgOverviewView(BaseInsightView):
    def get(self, request):
        return Response(services.get_org_overview(self.get_base_queryset()))


class CountrySummaryView(BaseInsightView):
    def get(self, request):
        return Response(list(services.get_country_salary_summary(self.get_base_queryset())))


class JobTitleSummaryView(BaseInsightView):
    def get(self, request):
        country = request.query_params.get("country")
        return Response(list(services.get_job_title_salary_by_country(
            self.get_base_queryset(), country=country
        )))


class DepartmentSummaryView(BaseInsightView):
    def get(self, request):
        return Response(list(services.get_department_salary_summary(self.get_base_queryset())))


class TopEarnersView(BaseInsightView):
    def get(self, request):
        limit = int(request.query_params.get("limit", 10))
        queryset = services.get_top_earners(self.get_base_queryset(), n=limit)
        return Response(EmployeeSerializer(queryset, many=True).data)