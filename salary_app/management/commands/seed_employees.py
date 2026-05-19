import random
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

from django.core.management.base import BaseCommand

from salary_app.models import Department, Employee, Role


COUNTRIES = [
    "India", "USA", "Germany", "UK", "Canada",
    "Australia", "Singapore", "Netherlands", "Brazil", "France",
]

JOB_TITLES = [
    "Software Engineer", "Senior Software Engineer", "Staff Engineer",
    "Product Manager", "Senior Product Manager",
    "Data Analyst", "Data Scientist", "ML Engineer",
    "Designer", "Senior Designer",
    "DevOps Engineer", "Platform Engineer",
    "QA Engineer", "Technical Lead",
    "HR Specialist", "Finance Analyst",
]

SALARY_RANGES = {
    "Software Engineer":        (50_000,  90_000),
    "Senior Software Engineer": (90_000, 130_000),
    "Staff Engineer":           (130_000, 180_000),
    "Product Manager":          (80_000, 120_000),
    "Senior Product Manager":   (120_000, 160_000),
    "Data Analyst":             (55_000,  85_000),
    "Data Scientist":           (90_000, 130_000),
    "ML Engineer":              (100_000, 150_000),
    "Designer":                 (55_000,  85_000),
    "Senior Designer":          (85_000, 120_000),
    "DevOps Engineer":          (80_000, 120_000),
    "Platform Engineer":        (90_000, 130_000),
    "QA Engineer":              (50_000,  80_000),
    "Technical Lead":           (120_000, 160_000),
    "HR Specialist":            (50_000,  80_000),
    "Finance Analyst":          (60_000,  95_000),
}

DEPARTMENTS_FOR_TITLE = {
    "Software Engineer":        Department.ENGINEERING,
    "Senior Software Engineer": Department.ENGINEERING,
    "Staff Engineer":           Department.ENGINEERING,
    "Product Manager":          Department.PRODUCT,
    "Senior Product Manager":   Department.PRODUCT,
    "Data Analyst":             Department.DATA,
    "Data Scientist":           Department.DATA,
    "ML Engineer":              Department.ENGINEERING,
    "Designer":                 Department.DESIGN,
    "Senior Designer":          Department.DESIGN,
    "DevOps Engineer":          Department.OPERATIONS,
    "Platform Engineer":        Department.ENGINEERING,
    "QA Engineer":              Department.ENGINEERING,
    "Technical Lead":           Department.ENGINEERING,
    "HR Specialist":            Department.HR,
    "Finance Analyst":          Department.FINANCE,
}


def random_hire_date():
    start = date(2018, 1, 1)
    end = date.today()
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def random_salary(job_title):
    low, high = SALARY_RANGES[job_title]
    return Decimal(str(random.randint(low, high)))


class Command(BaseCommand):
    help = "Seed the database with employees generated from first_names.txt and last_names.txt"

    def add_arguments(self, parser):
        parser.add_argument("--count",      type=int, default=10_000, help="Number of employees to create")
        parser.add_argument("--batch-size", type=int, default=500,    help="Bulk create batch size")
        parser.add_argument("--clear",      action="store_true",      help="Remove previously seeded employees first")
        parser.add_argument("--names-dir",type=str,default=None,
                            help="Directory containing first_names.txt and last_names.txt (default: data/)",
        )

    def handle(self, *args, **options):
        count = options["count"]
        batch_size = options["batch_size"]
        names_dir = (
            Path(options["names_dir"])
            if options["names_dir"]
            else Path(__file__).resolve().parents[3] / "data"
        )

        # ── Read name files once into memory ──────────────────────────────────
        first_names = (names_dir / "first_names.txt").read_text().splitlines()
        last_names  = (names_dir / "last_names.txt").read_text().splitlines()

        first_names = [n.strip() for n in first_names if n.strip()]
        last_names  = [n.strip() for n in last_names  if n.strip()]

        if not first_names or not last_names:
            self.stderr.write(self.style.ERROR("Name files are empty."))
            return

        # ── Clear previously seeded employees (user=None) ─────────────────────
        if options["clear"]:
            deleted, _ = Employee.objects.filter(user__isnull=True).delete()
            self.stdout.write(f"Cleared {deleted} previously seeded employees.")

        # ── Generate Employee objects in memory ───────────────────────────────
        employees = []
        for i in range(count):
            first_name = random.choice(first_names)
            last_name  = random.choice(last_names)
            job_title  = random.choice(JOB_TITLES)
            email      = f"{first_name.lower()}.{last_name.lower()}.{i}@company.com"

            employees.append(Employee(
                first_name=first_name,
                last_name=last_name,
                email=email,
                job_title=job_title,
                department=DEPARTMENTS_FOR_TITLE[job_title],
                country=random.choice(COUNTRIES),
                salary=random_salary(job_title),
                hire_date=random_hire_date(),
                role=Role.EMPLOYEE,
                is_active=True,
            ))

        # ── Bulk insert in batches ─────────────────────────────────────────────
        total_created = 0
        for i in range(0, len(employees), batch_size):
            batch = employees[i : i + batch_size]
            Employee.objects.bulk_create(batch, batch_size=batch_size)
            total_created += len(batch)
            self.stdout.write(f"  Inserted {total_created}/{count}...", ending="\r")

        self.stdout.write(self.style.SUCCESS(f"\nDone. Created {total_created} employees."))