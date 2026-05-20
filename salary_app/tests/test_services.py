#test services
import pytest
from decimal import Decimal

from salary_app.models import Employee, Department
from salary_app.services import (
    get_org_overview,
    get_country_salary_summary,
    get_job_title_salary_by_country,
    get_department_salary_summary,
    get_top_earners,
)


def make_employee(**kwargs):
    defaults = dict(
        job_title="Engineer",
        department=Department.ENGINEERING,
        hire_date="2023-01-01",
        is_active=True,
    )
    defaults.update(kwargs)
    return Employee.objects.create(**defaults)


# ── Org Overview ──────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_org_overview_returns_total_headcount():
    make_employee(first_name="A", last_name="One", email="a1@x.com", country="India", salary=Decimal("50000"))
    make_employee(first_name="B", last_name="Two", email="b2@x.com", country="USA",   salary=Decimal("90000"))
    make_employee(first_name="C", last_name="Three", email="c3@x.com", country="India", salary=Decimal("70000"))

    result = get_org_overview(Employee.objects.filter(is_active=True))

    assert result["total_employees"] == 3


@pytest.mark.django_db
def test_org_overview_returns_correct_min_max_avg():
    make_employee(first_name="A", last_name="One", email="a1@x.com", country="India", salary=Decimal("50000"))
    make_employee(first_name="B", last_name="Two", email="b2@x.com", country="USA",   salary=Decimal("90000"))
    make_employee(first_name="C", last_name="Three", email="c3@x.com", country="India", salary=Decimal("70000"))

    result = get_org_overview(Employee.objects.filter(is_active=True))

    assert result["min_salary"] == Decimal("50000")
    assert result["max_salary"] == Decimal("90000")
    assert result["avg_salary"] == Decimal("70000")


@pytest.mark.django_db
def test_org_overview_excludes_inactive_employees():
    make_employee(first_name="A", last_name="One", email="a1@x.com", country="India", salary=Decimal("50000"))
    make_employee(first_name="B", last_name="Two", email="b2@x.com", country="India", salary=Decimal("90000"), is_active=False)

    result = get_org_overview(Employee.objects.filter(is_active=True))

    assert result["total_employees"] == 1
    assert result["max_salary"] == Decimal("50000")


# ── Country Summary ───────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_country_summary_groups_by_country():
    make_employee(first_name="A", last_name="One", email="a1@x.com", country="India", salary=Decimal("50000"))
    make_employee(first_name="B", last_name="Two", email="b2@x.com", country="India", salary=Decimal("70000"))
    make_employee(first_name="C", last_name="Three", email="c3@x.com", country="USA",   salary=Decimal("90000"))

    results = list(get_country_salary_summary(Employee.objects.filter(is_active=True)))
    countries = [r["country"] for r in results]

    assert "India" in countries
    assert "USA" in countries
    assert len(results) == 2


@pytest.mark.django_db
def test_country_summary_correct_min_max_avg():
    make_employee(first_name="A", last_name="One", email="a1@x.com", country="India", salary=Decimal("40000"))
    make_employee(first_name="B", last_name="Two", email="b2@x.com", country="India", salary=Decimal("80000"))
    make_employee(first_name="C", last_name="Three", email="c3@x.com", country="India", salary=Decimal("60000"))

    results = {r["country"]: r for r in get_country_salary_summary(Employee.objects.filter(is_active=True))}
    india = results["India"]

    assert india["min_salary"] == Decimal("40000")
    assert india["max_salary"] == Decimal("80000")
    assert india["avg_salary"] == Decimal("60000")
    assert india["headcount"] == 3


# ── Job Title by Country ──────────────────────────────────────────────────────

@pytest.mark.django_db
def test_job_title_summary_returns_avg_per_title_and_country():
    make_employee(first_name="A", last_name="One", email="a1@x.com", country="India", job_title="Engineer", salary=Decimal("60000"))
    make_employee(first_name="B", last_name="Two", email="b2@x.com", country="India", job_title="Engineer", salary=Decimal("80000"))
    make_employee(first_name="C", last_name="Three", email="c3@x.com", country="India", job_title="Designer", salary=Decimal("55000"))

    results = {
        (r["job_title"], r["country"]): r
        for r in get_job_title_salary_by_country(Employee.objects.filter(is_active=True))
    }

    assert results[("Engineer", "India")]["avg_salary"] == Decimal("70000")
    assert results[("Designer", "India")]["headcount"] == 1


@pytest.mark.django_db
def test_job_title_summary_filters_by_country():
    make_employee(first_name="A", last_name="One", email="a1@x.com", country="India", job_title="Engineer", salary=Decimal("60000"))
    make_employee(first_name="B", last_name="Two", email="b2@x.com", country="USA",   job_title="Engineer", salary=Decimal("100000"))

    results = list(get_job_title_salary_by_country(Employee.objects.filter(is_active=True), country="India"))
    countries = [r["country"] for r in results]

    assert all(c == "India" for c in countries)
    assert "USA" not in countries


# ── Department Summary ────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_department_summary_groups_by_department():
    make_employee(first_name="A", last_name="One", email="a1@x.com", country="India", department=Department.ENGINEERING, salary=Decimal("70000"))
    make_employee(first_name="B", last_name="Two", email="b2@x.com", country="India", department=Department.ENGINEERING, salary=Decimal("90000"))
    make_employee(first_name="C", last_name="Three", email="c3@x.com", country="India", department=Department.FINANCE,     salary=Decimal("65000"))

    results = {r["department"]: r for r in get_department_salary_summary(Employee.objects.filter(is_active=True))}

    assert Department.ENGINEERING in results
    assert Department.FINANCE in results
    assert results[Department.ENGINEERING]["headcount"] == 2
    assert results[Department.FINANCE]["avg_salary"] == Decimal("65000")


# ── Top Earners ───────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_top_earners_returns_correct_count():
    for i in range(15):
        make_employee(
            first_name=f"Emp{i}", last_name="Test",
            email=f"emp{i}@x.com", country="India",
            salary=Decimal(str(50000 + i * 1000)),
        )

    results = list(get_top_earners(Employee.objects.filter(is_active=True), n=10))
    assert len(results) == 10


@pytest.mark.django_db
def test_top_earners_are_sorted_descending():
    make_employee(first_name="A", last_name="One", email="a1@x.com", country="India", salary=Decimal("50000"))
    make_employee(first_name="B", last_name="Two", email="b2@x.com", country="India", salary=Decimal("90000"))
    make_employee(first_name="C", last_name="Three", email="c3@x.com", country="India", salary=Decimal("70000"))

    results = list(get_top_earners(Employee.objects.filter(is_active=True), n=3))
    salaries = [r.salary for r in results]

    assert salaries == sorted(salaries, reverse=True)