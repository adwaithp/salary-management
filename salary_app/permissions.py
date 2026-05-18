from rest_framework.permissions import BasePermission, SAFE_METHODS

from salary_app.models import Role

PRIVILEGED_ROLES = {Role.HR, Role.ADMIN, Role.MANAGER}


def get_employee_profile(user):
    return getattr(user, "employee_profile", None)


def is_privileged(user):
    profile = get_employee_profile(user)
    return profile is not None and profile.role in PRIVILEGED_ROLES


class EmployeeAccessPermission(BasePermission):
    """
    HR / Admin / Manager — full CRUD on all employees.
    Employee             — read + update their own record only.
    Unauthenticated      — no access.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if is_privileged(request.user):
            return True

        # Employees are blocked from create
        if request.method == "POST":
            return False

        return True

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        if is_privileged(request.user):
            return True

        profile = get_employee_profile(request.user)
        if profile is None:
            return False

        # Employee can only access their own record
        return obj == profile