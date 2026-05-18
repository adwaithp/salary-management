from django.db import models


class Employee(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    job_title = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=12, decimal_places=2)
    hire_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["last_name", "first_name"]
        indexes = [
            models.Index(fields=["country"]),
            models.Index(fields=["job_title"]),
            models.Index(fields=["country", "job_title"]),
        ]

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name