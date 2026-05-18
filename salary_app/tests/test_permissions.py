import pytest
from decimal import Decimal
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from salary_app.models import Employee, Role, Department


# ── Fixtures ──────────────────────────────────────────────────────────────────

def make_employee(role, email, first_name="Test", last_name="User"):
    user = User.objects.create_user(username=email, email=email, password="pass123")
    employee = Employee.objects.create(
        user=user,
        first_name=first_name,
        last_name=last_name,
        email=email,
        job_title="Staff",
        department=Department.ENGINEERING,
        country="India",
        salary=Decimal("60000.00"),
        hire_date="2023-01-01",
        role=role,
    )
    return user, employee


def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def hr_client(db):
    user, _ = make_employee(Role.HR, "hr@example.com", "HR", "User")
    return auth_client(user)


@pytest.fixture
def manager_client(db):
    user, _ = make_employee(Role.MANAGER, "manager@example.com", "Manager", "User")
    return auth_client(user)


@pytest.fixture
def employee_user(db):
    user, employee = make_employee(Role.EMPLOYEE, "emp@example.com", "Emp", "User")
    return user, employee


@pytest.fixture
def employee_client(employee_user):
    user, _ = employee_user
    return auth_client(user)


@pytest.fixture
def another_employee(db):
    _, employee = make_employee(Role.EMPLOYEE, "other@example.com", "Other", "Person")
    return employee


@pytest.fixture
def anon_client():
    return APIClient()


# ── Unauthenticated ───────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_unauthenticated_cannot_list(anon_client):
    response = anon_client.get(reverse("employee-list"))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_unauthenticated_cannot_create(anon_client):
    response = anon_client.post(reverse("employee-list"), {})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ── HR permissions ────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_hr_can_list_all_employees(hr_client, another_employee):
    response = hr_client.get(reverse("employee-list"))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) >= 2


@pytest.mark.django_db
def test_hr_can_create_employee(hr_client):
    payload = {
        "first_name": "New",
        "last_name": "Employee",
        "email": "new@example.com",
        "job_title": "Engineer",
        "department": Department.ENGINEERING,
        "country": "India",
        "salary": "65000.00",
        "hire_date": "2024-01-01",
        "role": Role.EMPLOYEE,
    }
    response = hr_client.post(reverse("employee-list"), payload)
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_hr_can_update_any_employee(hr_client, another_employee):
    response = hr_client.patch(
        reverse("employee-detail", args=[another_employee.id]),
        {"job_title": "Senior Engineer"},
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_hr_can_delete_any_employee(hr_client, another_employee):
    response = hr_client.delete(reverse("employee-detail", args=[another_employee.id]))
    assert response.status_code == status.HTTP_204_NO_CONTENT


# ── Manager permissions ───────────────────────────────────────────────────────

@pytest.mark.django_db
def test_manager_can_list_all_employees(manager_client, another_employee):
    response = manager_client.get(reverse("employee-list"))
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_manager_can_create_employee(manager_client):
    payload = {
        "first_name": "New",
        "last_name": "Hire",
        "email": "newhire@example.com",
        "job_title": "Analyst",
        "department": Department.FINANCE,
        "country": "USA",
        "salary": "55000.00",
        "hire_date": "2024-01-01",
        "role": Role.EMPLOYEE,
    }
    response = manager_client.post(reverse("employee-list"), payload)
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_manager_can_update_employee(manager_client, another_employee):
    response = manager_client.patch(
        reverse("employee-detail", args=[another_employee.id]),
        {"salary": "70000.00"},
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_manager_can_delete_employee(manager_client, another_employee):
    response = manager_client.delete(reverse("employee-detail", args=[another_employee.id]))
    assert response.status_code == status.HTTP_204_NO_CONTENT


# ── Employee permissions ──────────────────────────────────────────────────────

@pytest.mark.django_db
def test_employee_can_view_own_profile(employee_client, employee_user):
    _, employee = employee_user
    response = employee_client.get(reverse("employee-detail", args=[employee.id]))
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_employee_cannot_view_other_profiles(employee_client, another_employee):
    # Other employees are outside the queryset — 404 is correct and more secure
    # (does not leak that the record exists)
    response = employee_client.get(reverse("employee-detail", args=[another_employee.id]))
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_employee_can_update_own_profile(employee_client, employee_user):
    _, employee = employee_user
    response = employee_client.patch(
        reverse("employee-detail", args=[employee.id]),
        {"country": "Germany"},
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_employee_cannot_update_other_profiles(employee_client, another_employee):
    # Other employees are outside the queryset — 404
    response = employee_client.patch(
        reverse("employee-detail", args=[another_employee.id]),
        {"country": "Germany"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_employee_cannot_create_employees(employee_client):
    payload = {
        "first_name": "Sneaky",
        "last_name": "User",
        "email": "sneaky@example.com",
        "job_title": "Engineer",
        "department": Department.ENGINEERING,
        "country": "India",
        "salary": "60000.00",
        "hire_date": "2024-01-01",
    }
    response = employee_client.post(reverse("employee-list"), payload)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_employee_cannot_delete_employees(employee_client, another_employee):
    # Other employees are outside the queryset — 404
    response = employee_client.delete(reverse("employee-detail", args=[another_employee.id]))
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_employee_list_only_shows_own_profile(employee_client, employee_user, another_employee):
    _, employee = employee_user
    response = employee_client.get(reverse("employee-list"))
    assert response.status_code == status.HTTP_200_OK
    ids = [e["id"] for e in response.data]
    assert employee.id in ids
    assert another_employee.id not in ids