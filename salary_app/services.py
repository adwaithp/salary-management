#services.py
from django.db.models import Avg, Count, Max, Min, QuerySet


def get_org_overview(queryset: QuerySet) -> dict:
    """Org-wide totals — total headcount, avg, min, max salary."""
    return queryset.aggregate(
        total_employees=Count("id"),
        avg_salary=Avg("salary"),
        min_salary=Min("salary"),
        max_salary=Max("salary"),
    )


def get_country_salary_summary(queryset: QuerySet) -> QuerySet:
    """Min, max, avg salary and headcount grouped by country."""
    return (
        queryset
        .values("country")
        .annotate(
            min_salary=Min("salary"),
            max_salary=Max("salary"),
            avg_salary=Avg("salary"),
            headcount=Count("id"),
        )
        .order_by("country")
    )


def get_job_title_salary_by_country(queryset: QuerySet, country: str = None) -> QuerySet:
    """Avg salary per job title per country, optionally filtered to one country."""
    if country:
        queryset = queryset.filter(country=country)
    return (
        queryset
        .values("job_title", "country")
        .annotate(
            avg_salary=Avg("salary"),
            headcount=Count("id"),
        )
        .order_by("country", "job_title")
    )


def get_department_salary_summary(queryset: QuerySet) -> QuerySet:
    """Min, max, avg salary and headcount grouped by department."""
    return (
        queryset
        .values("department")
        .annotate(
            min_salary=Min("salary"),
            max_salary=Max("salary"),
            avg_salary=Avg("salary"),
            headcount=Count("id"),
        )
        .order_by("department")
    )


def get_top_earners(queryset: QuerySet, n: int = 10) -> QuerySet:
    """Top N employees by salary, descending."""
    return queryset.order_by("-salary")[:n]