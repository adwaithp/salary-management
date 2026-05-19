import pytest
from decimal import Decimal
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from salary_app.models import Employee, Department, Role


@pytest.fixture
def api_client():
    return APIClient()


def create_user_with_employee(email, password, role=Role.EMPLOYEE):
    user = User.objects.create_user(username=email, email=email, password=password)
    employee = Employee.objects.create(
        user=user,
        first_name="Test",
        last_name="User",
        email=email,
        job_title="Engineer",
        department=Department.ENGINEERING,
        country="India",
        salary=Decimal("60000.00"),
        hire_date="2023-01-01",
        role=role,
    )
    return user, employee


# ── Login ─────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_login_returns_access_and_refresh_tokens(api_client):
    create_user_with_employee("alice@example.com", "securepass123")
    response = api_client.post(reverse("token_obtain_pair"), {
        "username": "alice@example.com",
        "password": "securepass123",
    })
    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data
    assert "refresh" in response.data


@pytest.mark.django_db
def test_login_wrong_password_returns_401(api_client):
    create_user_with_employee("bob@example.com", "correctpass")
    response = api_client.post(reverse("token_obtain_pair"), {
        "username": "bob@example.com",
        "password": "wrongpass",
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_login_nonexistent_user_returns_401(api_client):
    response = api_client.post(reverse("token_obtain_pair"), {
        "username": "ghost@example.com",
        "password": "anypass",
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_access_token_allows_authenticated_request(api_client):
    create_user_with_employee("carol@example.com", "pass12345")
    login = api_client.post(reverse("token_obtain_pair"), {
        "username": "carol@example.com",
        "password": "pass12345",
    })
    token = login.data["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    response = api_client.get(reverse("employee-list"))
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_no_public_register_endpoint_exists(api_client):
    response = api_client.post("/api/auth/register/", {})
    assert response.status_code == status.HTTP_404_NOT_FOUND


# ── HR creating employee accounts ─────────────────────────────────────────────

@pytest.mark.django_db
def test_hr_can_create_employee_with_password(api_client):
    _, hr_employee = create_user_with_employee("hr@example.com", "hrpass123", role=Role.HR)
    api_client.force_authenticate(user=hr_employee.user)

    response = api_client.post(reverse("employee-list"), {
        "first_name": "New",
        "last_name": "Hire",
        "email": "newhire@example.com",
        "password": "temppass123",
        "job_title": "Developer",
        "department": Department.ENGINEERING,
        "country": "India",
        "salary": "65000.00",
        "hire_date": "2024-01-01",
        "role": Role.EMPLOYEE,
    })
    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.filter(username="newhire@example.com").exists()


@pytest.mark.django_db
def test_created_employee_can_login(api_client):
    _, hr_employee = create_user_with_employee("hr@example.com", "hrpass123", role=Role.HR)
    api_client.force_authenticate(user=hr_employee.user)

    api_client.post(reverse("employee-list"), {
        "first_name": "New",
        "last_name": "Hire",
        "email": "newhire@example.com",
        "password": "temppass123",
        "job_title": "Developer",
        "department": Department.ENGINEERING,
        "country": "India",
        "salary": "65000.00",
        "hire_date": "2024-01-01",
        "role": Role.EMPLOYEE,
    })

    api_client.credentials()
    response = api_client.post(reverse("token_obtain_pair"), {
        "username": "newhire@example.com",
        "password": "temppass123",
    })
    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data


@pytest.mark.django_db
def test_create_employee_without_password_returns_400(api_client):
    _, hr_employee = create_user_with_employee("hr@example.com", "hrpass123", role=Role.HR)
    api_client.force_authenticate(user=hr_employee.user)

    response = api_client.post(reverse("employee-list"), {
        "first_name": "No",
        "last_name": "Password",
        "email": "nopass@example.com",
        "job_title": "Developer",
        "department": Department.ENGINEERING,
        "country": "India",
        "salary": "65000.00",
        "hire_date": "2024-01-01",
        "role": Role.EMPLOYEE,
    })
    assert response.status_code == status.HTTP_400_BAD_REQUEST