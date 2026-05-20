#test seed employee
import pytest
from decimal import Decimal
from django.contrib.auth.models import User
from django.core.management import call_command

from salary_app.models import Employee, Department


@pytest.fixture
def names_dir(tmp_path):
    (tmp_path / "first_names.txt").write_text("Alice\nBob\nCarol\nDan\nEve")
    (tmp_path / "last_names.txt").write_text("Smith\nJones\nBrown\nDavis\nWilson")
    return str(tmp_path)


@pytest.mark.django_db
def test_seed_creates_correct_number_of_employees(names_dir):
    call_command("seed_employees", count=10, names_dir=names_dir)
    assert Employee.objects.count() == 10


@pytest.mark.django_db
def test_seed_employees_have_no_linked_user(names_dir):
    call_command("seed_employees", count=5, names_dir=names_dir)
    assert Employee.objects.filter(user__isnull=True).count() == 5


@pytest.mark.django_db
def test_seed_emails_are_unique(names_dir):
    call_command("seed_employees", count=20, names_dir=names_dir)
    total = Employee.objects.count()
    assert total == Employee.objects.values("email").distinct().count()


@pytest.mark.django_db
def test_seed_names_come_from_name_files(names_dir):
    call_command("seed_employees", count=10, names_dir=names_dir)
    first_names = {"Alice", "Bob", "Carol", "Dan", "Eve"}
    last_names = {"Smith", "Jones", "Brown", "Davis", "Wilson"}
    for employee in Employee.objects.all():
        assert employee.first_name in first_names
        assert employee.last_name in last_names


@pytest.mark.django_db
def test_seed_all_employees_are_active(names_dir):
    call_command("seed_employees", count=10, names_dir=names_dir)
    assert Employee.objects.filter(is_active=False).count() == 0


@pytest.mark.django_db
def test_seed_clear_flag_removes_previous_seeded_employees(names_dir):
    call_command("seed_employees", count=10, names_dir=names_dir)
    call_command("seed_employees", count=5, names_dir=names_dir, clear=True)
    assert Employee.objects.count() == 5


@pytest.mark.django_db
def test_seed_clear_does_not_remove_real_employees(names_dir):
    user = User.objects.create_user(username="real@x.com", email="real@x.com", password="pass")
    Employee.objects.create(
        user=user, first_name="Real", last_name="Employee", email="real@x.com",
        job_title="Engineer", department=Department.ENGINEERING,
        country="India", salary=Decimal("70000"), hire_date="2023-01-01",
    )
    call_command("seed_employees", count=5, names_dir=names_dir, clear=True)
    assert Employee.objects.filter(email="real@x.com").exists()
    assert Employee.objects.count() == 6


@pytest.mark.django_db
def test_seed_is_idempotent_with_clear_flag(names_dir):
    call_command("seed_employees", count=10, names_dir=names_dir)
    call_command("seed_employees", count=10, names_dir=names_dir, clear=True)
    call_command("seed_employees", count=10, names_dir=names_dir, clear=True)
    assert Employee.objects.count() == 10