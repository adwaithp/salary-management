import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from salary_app.models import Employee, Role, Department


@pytest.mark.django_db
def test_employee_can_be_created_with_required_fields():
    employee = Employee.objects.create(
        first_name="Alice",
        last_name="Johnson",
        email="alice@example.com",
        job_title="Software Engineer",
        department=Department.ENGINEERING,
        country="India",
        salary=Decimal("75000.00"),
        hire_date="2023-01-15",
    )
    assert employee.pk is not None


@pytest.mark.django_db
def test_full_name_property_combines_first_and_last():
    employee = Employee(first_name="Bob", last_name="Smith")
    assert employee.full_name == "Bob Smith"


@pytest.mark.django_db
def test_str_returns_full_name():
    employee = Employee(first_name="Bob", last_name="Smith")
    assert str(employee) == "Bob Smith"


@pytest.mark.django_db
def test_role_defaults_to_employee():
    employee = Employee.objects.create(
        first_name="Dan",
        last_name="Brown",
        email="dan@example.com",
        job_title="Analyst",
        department=Department.FINANCE,
        country="USA",
        salary=Decimal("55000.00"),
        hire_date="2021-03-10",
    )
    assert employee.role == Role.EMPLOYEE


@pytest.mark.django_db
def test_role_can_be_set_to_hr():
    employee = Employee.objects.create(
        first_name="Grace",
        last_name="Hall",
        email="grace@example.com",
        job_title="HR Specialist",
        department=Department.HR,
        country="India",
        salary=Decimal("70000.00"),
        hire_date="2022-03-01",
        role=Role.HR,
    )
    assert employee.role == Role.HR


@pytest.mark.django_db
def test_invalid_role_raises_validation_error():
    employee = Employee(
        first_name="Bad",
        last_name="Role",
        email="bad@example.com",
        job_title="Ghost",
        department=Department.ENGINEERING,
        country="India",
        salary=Decimal("50000.00"),
        hire_date="2023-01-01",
        role="ghost",
    )
    with pytest.raises(ValidationError):
        employee.full_clean()


@pytest.mark.django_db
def test_invalid_department_raises_validation_error():
    employee = Employee(
        first_name="Bad",
        last_name="Dept",
        email="baddept@example.com",
        job_title="Engineer",
        department="unknown_dept",
        country="India",
        salary=Decimal("50000.00"),
        hire_date="2023-01-01",
    )
    with pytest.raises(ValidationError):
        employee.full_clean()


@pytest.mark.django_db
def test_salary_is_stored_as_decimal():
    employee = Employee.objects.create(
        first_name="Carol",
        last_name="White",
        email="carol@example.com",
        job_title="Designer",
        department=Department.DESIGN,
        country="Germany",
        salary=Decimal("60000.50"),
        hire_date="2022-06-01",
    )
    fetched = Employee.objects.get(pk=employee.pk)
    assert fetched.salary == Decimal("60000.50")
    assert isinstance(fetched.salary, Decimal)


@pytest.mark.django_db
def test_is_active_defaults_to_true():
    employee = Employee.objects.create(
        first_name="Eve",
        last_name="Davis",
        email="eve@example.com",
        job_title="Manager",
        department=Department.HR,
        country="UK",
        salary=Decimal("90000.00"),
        hire_date="2020-09-01",
    )
    assert employee.is_active is True


@pytest.mark.django_db
def test_email_must_be_unique():
    Employee.objects.create(
        first_name="Frank",
        last_name="Lee",
        email="duplicate@example.com",
        job_title="DevOps",
        department=Department.ENGINEERING,
        country="Canada",
        salary=Decimal("80000.00"),
        hire_date="2023-04-20",
    )
    with pytest.raises(IntegrityError):
        Employee.objects.create(
            first_name="Another",
            last_name="Person",
            email="duplicate@example.com",
            job_title="QA",
            department=Department.ENGINEERING,
            country="India",
            salary=Decimal("50000.00"),
            hire_date="2023-07-01",
        )


@pytest.mark.django_db
def test_first_name_cannot_be_blank():
    employee = Employee(
        first_name="",
        last_name="Smith",
        email="test@example.com",
        job_title="Engineer",
        department=Department.ENGINEERING,
        country="India",
        salary=Decimal("50000.00"),
        hire_date="2023-01-01",
    )
    with pytest.raises(ValidationError):
        employee.full_clean()


@pytest.mark.django_db
def test_last_name_cannot_be_blank():
    employee = Employee(
        first_name="John",
        last_name="",
        email="test2@example.com",
        job_title="Engineer",
        department=Department.ENGINEERING,
        country="India",
        salary=Decimal("50000.00"),
        hire_date="2023-01-01",
    )
    with pytest.raises(ValidationError):
        employee.full_clean()


@pytest.mark.django_db
def test_employees_ordered_by_last_name_then_first_name():
    Employee.objects.create(
        first_name="Zara", last_name="Ahmed", email="zara@example.com",
        job_title="PM", department=Department.PRODUCT, country="India",
        salary=Decimal("70000.00"), hire_date="2023-01-01",
    )
    Employee.objects.create(
        first_name="Aaron", last_name="Chen", email="aaron@example.com",
        job_title="PM", department=Department.PRODUCT, country="India",
        salary=Decimal("72000.00"), hire_date="2023-01-01",
    )
    Employee.objects.create(
        first_name="Beth", last_name="Ahmed", email="beth@example.com",
        job_title="Engineer", department=Department.ENGINEERING, country="India",
        salary=Decimal("68000.00"), hire_date="2023-01-01",
    )
    employees = list(Employee.objects.values_list("last_name", "first_name"))
    assert employees == sorted(employees)