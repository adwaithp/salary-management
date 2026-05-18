from django.contrib import admin
from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from salary_app.views import EmployeeViewSet, OrgOverviewView, CountrySummaryView, JobTitleSummaryView, \
    DepartmentSummaryView, TopEarnersView

router = DefaultRouter()
router.register(r"employees", EmployeeViewSet, basename="employee")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("insights/overview/", OrgOverviewView.as_view(), name="insights-overview"),
    path("insights/by-country/", CountrySummaryView.as_view(), name="insights-country-summary"),
    path("insights/by-job-title/", JobTitleSummaryView.as_view(), name="insights-job-title-summary"),
    path("insights/by-department/", DepartmentSummaryView.as_view(), name="insights-department-summary"),
    path("insights/top-earners/", TopEarnersView.as_view(), name="insights-top-earners"),
    *router.urls,
]