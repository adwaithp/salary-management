import pytest
from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import CommandError
from io import StringIO

from salary_app.models import Employee, Role, Department


@pytest.mark.django_db
def test_creates_django_user():
    call_command("create_hr_user",
                 email="hr@example.com",
                 password="securepass123",
                 first_name="Jane",
                 last_name="Doe")
    assert User.objects.filter(username="hr@example.com").exists()


@pytest.mark.django_db
def test_creates_employee_with_hr_role_by_default():
    call_command("create_hr_user",
                 email="hr@example.com",
                 password="securepass123",
                 first_name="Jane",
                 last_name="Doe")
    employee = Employee.objects.get(email="hr@example.com")
    assert employee.role == Role.HR


@pytest.mark.django_db
def test_creates_employee_with_admin_role():
    call_command("create_hr_user",
                 email="admin@example.com",
                 password="securepass123",
                 first_name="Super",
                 last_name="Admin",
                 role="admin")
    employee = Employee.objects.get(email="admin@example.com")
    assert employee.role == Role.ADMIN


@pytest.mark.django_db
def test_links_user_to_employee():
    call_command("create_hr_user",
                 email="hr@example.com",
                 password="securepass123",
                 first_name="Jane",
                 last_name="Doe")
    employee = Employee.objects.get(email="hr@example.com")
    assert employee.user is not None
    assert employee.user.username == "hr@example.com"


@pytest.mark.django_db
def test_created_user_can_authenticate():
    call_command("create_hr_user",
                 email="hr@example.com",
                 password="securepass123",
                 first_name="Jane",
                 last_name="Doe")
    from django.contrib.auth import authenticate
    user = authenticate(username="hr@example.com", password="securepass123")
    assert user is not None


@pytest.mark.django_db
def test_duplicate_email_prints_error_and_does_not_raise():
    call_command("create_hr_user",
                 email="hr@example.com",
                 password="pass123",
                 first_name="Jane",
                 last_name="Doe")
    err = StringIO()
    call_command("create_hr_user",
                 email="hr@example.com",
                 password="pass456",
                 first_name="Jane",
                 last_name="Doe",
                 stderr=err)
    assert "already exists" in err.getvalue()
    assert User.objects.filter(username="hr@example.com").count() == 1