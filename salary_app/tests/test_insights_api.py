import pytest
from decimal import Decimal
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from salary_app.models import Employee, Department, Role


def make_employee(role=Role.EMPLOYEE, **kwargs):
    email = kwargs.pop("email")
    user = User.objects.create_user(username=email, email=email, password="pass")
    defaults = dict(
        job_title="Engineer",
        department=Department.ENGINEERING,
        hire_date="2023-01-01",
        role=role,
        is_active=True,
    )
    defaults.update(kwargs)
    return Employee.objects.create(user=user, email=email, **defaults)


@pytest.fixture
def hr_client(db):
    emp = make_employee(role=Role.HR, first_name="HR", last_name="User", email="hr@x.com",
                        country="India", salary=Decimal("80000"), job_title="HR Manager")
    client = APIClient()
    client.force_authenticate(user=emp.user)
    return client


@pytest.fixture
def employee_client(db):
    emp = make_employee(first_name="Emp", last_name="User", email="emp@x.com",
                        country="India", salary=Decimal("60000"))
    client = APIClient()
    client.force_authenticate(user=emp.user)
    return client


@pytest.fixture
def sample_employees(db):
    make_employee(first_name="Alice", last_name="A", email="alice@x.com", country="India",
                  job_title="Engineer",  department=Department.ENGINEERING, salary=Decimal("50000"))
    make_employee(first_name="Bob",   last_name="B", email="bob@x.com",   country="India",
                  job_title="Engineer",  department=Department.ENGINEERING, salary=Decimal("90000"))
    make_employee(first_name="Carol", last_name="C", email="carol@x.com", country="India",
                  job_title="Designer",  department=Department.DESIGN,       salary=Decimal("60000"))
    make_employee(first_name="Dan",   last_name="D", email="dan@x.com",   country="USA",
                  job_title="Engineer",  department=Department.ENGINEERING, salary=Decimal("120000"))


# ── Access control ────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_unauthenticated_cannot_access_insights():
    client = APIClient()
    assert client.get(reverse("insights-overview")).status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_hr_can_access_insights(hr_client):
    assert hr_client.get(reverse("insights-overview")).status_code == status.HTTP_200_OK


# ── Org overview ──────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_overview_returns_expected_fields(hr_client, sample_employees):
    response = hr_client.get(reverse("insights-overview"))
    data = response.data
    assert "total_employees" in data
    assert "avg_salary" in data
    assert "min_salary" in data
    assert "max_salary" in data


@pytest.mark.django_db
def test_overview_headcount_is_correct(hr_client, sample_employees):
    response = hr_client.get(reverse("insights-overview"))
    # 4 sample + 1 hr_client fixture employee
    assert response.data["total_employees"] == 5


# ── Country summary ───────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_country_summary_returns_200(hr_client, sample_employees):
    response = hr_client.get(reverse("insights-country-summary"))
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_country_summary_has_expected_fields(hr_client, sample_employees):
    response = hr_client.get(reverse("insights-country-summary"))
    first = response.data[0]
    assert "country" in first
    assert "min_salary" in first
    assert "max_salary" in first
    assert "avg_salary" in first
    assert "headcount" in first


@pytest.mark.django_db
def test_country_summary_correct_values_for_india(hr_client, sample_employees):
    response = hr_client.get(reverse("insights-country-summary"))
    india = next(r for r in response.data if r["country"] == "India")
    # India has: 50k, 90k, 60k (sample) + 80k (hr_client fixture) = 4 employees
    assert india["headcount"] == 4
    assert Decimal(india["min_salary"]) == Decimal("50000")
    assert Decimal(india["max_salary"]) == Decimal("90000")


# ── Job title by country ──────────────────────────────────────────────────────

@pytest.mark.django_db
def test_job_title_summary_returns_200(hr_client, sample_employees):
    response = hr_client.get(reverse("insights-job-title-summary"))
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_job_title_summary_filters_by_country(hr_client, sample_employees):
    response = hr_client.get(reverse("insights-job-title-summary"), {"country": "India"})
    countries = [r["country"] for r in response.data]
    assert all(c == "India" for c in countries)


@pytest.mark.django_db
def test_job_title_summary_correct_avg_for_engineer_india(hr_client, sample_employees):
    response = hr_client.get(reverse("insights-job-title-summary"), {"country": "India"})
    engineer = next(r for r in response.data if r["job_title"] == "Engineer")
    # Alice: 50k, Bob: 90k → avg = 70k (HR user has job_title="HR Manager", not counted)
    assert Decimal(engineer["avg_salary"]) == Decimal("70000")


# ── Department summary ────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_department_summary_returns_200(hr_client, sample_employees):
    response = hr_client.get(reverse("insights-department-summary"))
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_department_summary_has_expected_fields(hr_client, sample_employees):
    response = hr_client.get(reverse("insights-department-summary"))
    first = response.data[0]
    assert "department" in first
    assert "headcount" in first
    assert "avg_salary" in first


# ── Top earners ───────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_top_earners_returns_200(hr_client, sample_employees):
    response = hr_client.get(reverse("insights-top-earners"))
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_top_earners_sorted_descending(hr_client, sample_employees):
    response = hr_client.get(reverse("insights-top-earners"))
    salaries = [Decimal(e["salary"]) for e in response.data]
    assert salaries == sorted(salaries, reverse=True)


@pytest.mark.django_db
def test_top_earners_respects_limit_param(hr_client, sample_employees):
    response = hr_client.get(reverse("insights-top-earners"), {"limit": 2})
    assert len(response.data) == 2