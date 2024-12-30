# models.py
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models

from departments.models import Department

CUSTOM_PERMISSIONS = {
    "employee_list": "Can list all employees",
    "employee_update": "Can update all employees",
    "employee_create": "Can create employees",
    "employee_destroy": "Can delete employees",
    "salary_view_all": "Can view salaries of all employees",
    "salary_update": "Can update salaries",
    "salary_delete": "Can delete salaries",
    "leave_view_all": "Can view all leave requests",
    "leave_update_status": "Can update leave status",
    "leave_delete": "Can delete leave records",
    "department_create": "Can create departments",
    "department_view_all": "Can view all departments",
    "department_delete": "Can delete departments",
    "department_update": "Can update departments",
}

class Role(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(max_length=255, blank=True, null=True)
    permissions = ArrayField(
        models.CharField(
            max_length=255,
            choices=[(value, value) for value in CUSTOM_PERMISSIONS.values()], 
        ),
        blank=True,
        null=True,
        help_text="List of permissions assigned to this role",
    )

    def __str__(self):
        return self.name

    def get_permission_keys(self):
        return [key for key, value in CUSTOM_PERMISSIONS.items() if value in self.permissions]

    def set_permissions_from_keys(self, permission_keys):
        self.permissions = [CUSTOM_PERMISSIONS[key] for key in permission_keys if key in CUSTOM_PERMISSIONS]

class Employee(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    manager = models.BooleanField(null=True, blank=True, default=False)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="employees",
        help_text="Each employee must belong to one department",
    )
    hire_date = models.DateField(null=True, blank=True)


class Salary(models.Model):
    id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="salaries"
    )
    pay_rate = models.DecimalField(max_digits=10, decimal_places=2)
    pay_period = models.CharField(max_length=50, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Salary for {self.employee.user.username}"


class Leave(models.Model):
    LEAVE_STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Cancelled", "Cancelled"),
    ]

    id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="leaves"
    )
    leave_type = models.CharField(max_length=100, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    reason = models.TextField(null=True, blank=True)
    status = models.CharField(
        max_length=10, choices=LEAVE_STATUS_CHOICES, default="Pending"
    )

    def __str__(self):
        return f"Leave ({self.leave_type}) for {self.employee.user.username}"
