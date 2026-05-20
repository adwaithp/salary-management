#create hr user
from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from salary_app.models import Department, Employee


class Command(BaseCommand):
    help = "Create an HR user with a linked Employee profile"

    def add_arguments(self, parser):
        parser.add_argument("--email",      required=True,  help="Login email")
        parser.add_argument("--password",   required=True,  help="Login password")
        parser.add_argument("--first-name", required=True,  dest="first_name")
        parser.add_argument("--last-name",  required=True,  dest="last_name")
        parser.add_argument("--job-title",  default="HR Manager", dest="job_title")
        parser.add_argument("--department", default=Department.HR)
        parser.add_argument("--country",    default="")
        parser.add_argument("--salary",     default="0.00")

    def handle(self, *args, **options):
        email = options["email"]

        if User.objects.filter(username=email).exists():
            self.stderr.write(self.style.ERROR(
                f"User with email '{email}' already exists."
            ))
            return

        user = User.objects.create_user(
            username=email,
            email=email,
            password=options["password"],
            first_name=options["first_name"],
            last_name=options["last_name"],
        )

        employee = Employee.objects.create(
            user=user,
            first_name=options["first_name"],
            last_name=options["last_name"],
            email=email,
            job_title=options["job_title"],
            department=options["department"],
            country=options["country"],
            salary=Decimal(options["salary"]),
            hire_date=date.today(),
        )

        self.stdout.write(self.style.SUCCESS(
            f"Created HR user: {employee.full_name} ({email})"
        ))