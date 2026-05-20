import pytest
from decimal import Decimal
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from salary_app.models import Employee, Department


@pytest.fixture
def api_client():
    return APIClient()


def create_hr_user(email, password):
    user = User.objects.create_user(username=email, email=email, password=password)
    Employee.objects.create(
        user=user, first_name="HR", last_name="User", email=email,
        job_title="HR Manager", department=Department.HR,
        country="India", salary=Decimal("80000.00"), hire_date="2023-01-01",
    )
    return user


@pytest.mark.django_db
def test_login_returns_access_and_refresh_tokens(api_client):
    create_hr_user("hr@example.com", "securepass123")
    response = api_client.post(reverse("token_obtain_pair"), {
        "username": "hr@example.com", "password": "securepass123",
    })
    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data
    assert "refresh" in response.data


@pytest.mark.django_db
def test_login_wrong_password_returns_401(api_client):
    create_hr_user("hr@example.com", "correctpass")
    response = api_client.post(reverse("token_obtain_pair"), {
        "username": "hr@example.com", "password": "wrongpass",
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_login_nonexistent_user_returns_401(api_client):
    response = api_client.post(reverse("token_obtain_pair"), {
        "username": "ghost@example.com", "password": "anypass",
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_access_token_allows_authenticated_request(api_client):
    user = create_hr_user("hr@example.com", "pass12345")
    login = api_client.post(reverse("token_obtain_pair"), {
        "username": "hr@example.com", "password": "pass12345",
    })
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
    assert api_client.get(reverse("employee-list")).status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_unauthenticated_cannot_access(api_client):
    assert api_client.get(reverse("employee-list")).status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_no_public_register_endpoint_exists(api_client):
    assert api_client.post("/api/auth/register/", {}).status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_authenticated_user_can_create_employee(api_client):
    user = create_hr_user("hr@example.com", "hrpass123")
    api_client.force_authenticate(user=user)
    response = api_client.post(reverse("employee-list"), {
        "first_name": "New", "last_name": "Hire",
        "email": "newhire@example.com",
        "job_title": "Developer", "department": Department.ENGINEERING,
        "country": "India", "salary": "65000.00", "hire_date": "2024-01-01",
    })
    assert response.status_code == status.HTTP_201_CREATED
    assert Employee.objects.filter(email="newhire@example.com").exists()


@pytest.mark.django_db
def test_unauthenticated_cannot_create_employee(api_client):
    response = api_client.post(reverse("employee-list"), {
        "first_name": "Ghost", "last_name": "User",
        "email": "ghost@example.com",
        "job_title": "Developer", "department": Department.ENGINEERING,
        "country": "India", "salary": "65000.00", "hire_date": "2024-01-01",
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED