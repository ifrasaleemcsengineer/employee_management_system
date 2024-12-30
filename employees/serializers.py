from django.contrib.auth.models import Permission
from django.db import transaction
from django.utils.timezone import now
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from authentication.models import User
from authentication.serializers import UserSerializer
from departments.models import Department
from departments.serializers import DepartmentSerializer

from .models import Employee, Leave, Role, Salary


class EmployeeDetailedSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    department = DepartmentSerializer()

    class Meta:
        model = Employee
        fields = ["id", "hire_date", "department", "user"]


class SalarySerializer(serializers.ModelSerializer):
    employee = EmployeeDetailedSerializer(read_only=True)

    class Meta:
        model = Salary
        fields = ["id", "pay_rate", "pay_period", "start_date", "end_date", "employee"]

    def update(self, instance, validated_data):
        has_changes = any(
            getattr(instance, field) != value for field, value in validated_data.items()
        )
        if has_changes:
            new_salary_data = {**validated_data, "employee": instance.employee}
            new_salary = Salary.objects.create(**new_salary_data)
            return new_salary
        else:
            return instance


class RoleSerializer(serializers.ModelSerializer):
    permissions_display = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = ["id", "name", "description", "permissions", "permissions_display"]

    def get_permissions_display(self, obj):
        permissions = Permission.objects.filter(codename__in=obj.permissions or [])
        return [{"codename": perm.codename, "name": perm.name} for perm in permissions]


class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    role = RoleSerializer(write_only=True, required=False)
    salary = SalarySerializer(write_only=True, required=False)
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), required=True
    )

    class Meta:
        model = Employee
        fields = [
            "id",
            "user",
            "department",
            "hire_date",
            "manager",
            "role",
            "salary",
        ]

    def to_representation(self, instance):
        """
        Customize the serialized output to include detailed department information.
        """
        representation = super().to_representation(instance)
        department = instance.department
        if department:
            representation["department"] = {
                "id": department.id,
                "name": department.name,
                "manager": (
                    {
                        "id": department.manager.id if department.manager else None,
                        "user": (
                            {
                                "id": (
                                    department.manager.id
                                    if department.manager
                                    else None
                                ),
                                "username": (
                                    department.manager.username
                                    if department.manager
                                    else None
                                ),
                                "first_name": (
                                    department.manager.first_name
                                    if department.manager
                                    else None
                                ),
                                "last_name": (
                                    department.manager.last_name
                                    if department.manager
                                    else None
                                ),
                            }
                            if department.manager
                            else None
                        ),
                    }
                    if department.manager
                    else None
                ),
            }
        return representation

    @transaction.atomic
    def create(self, validated_data):
        user_data = validated_data.pop("user")
        role_data = validated_data.pop("role", None)
        salary_data = validated_data.pop("salary", None)
        department = validated_data.pop("department", None)

        if not department:
            raise ValidationError(
                {"detail": "Department is required to create an employee."}
            )

        if validated_data.get("manager", False) and department.manager:
            raise ValidationError(
                {
                    "detail": f"This department already has a manager: {department.manager.username}."
                }
            )

        try:
            user_serializer = UserSerializer(data=user_data)
            user_serializer.is_valid(raise_exception=True)
            user = user_serializer.save()

            if role_data:
                role = Role.objects.create(
                    name=role_data["name"],
                    description=role_data.get("description", ""),
                    permissions=role_data.get("permissions", []),
                )
                user.role = role
                user.save()

            employee = Employee.objects.create(
                user=user, department=department, **validated_data
            )

            if validated_data.get("manager", False):
                department.manager = user
                department.save()

            if salary_data:
                Salary.objects.create(employee=employee, **salary_data)

            return employee

        except ValidationError as e:
            transaction.set_rollback(True)
            raise e

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", None)
        role_data = validated_data.pop("role", None)

        if user_data:
            user_serializer = UserSerializer(
                instance.user, data=user_data, partial=True
            )
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

        instance.department = validated_data.get("department", instance.department)
        instance.hire_date = validated_data.get("hire_date", instance.hire_date)

        new_manager_status = validated_data.get("manager", instance.manager)
        if new_manager_status:
            department = instance.department
            existing_manager = department.manager

            if existing_manager and existing_manager != instance:
                raise ValidationError(
                    {"manager": "This department already has a manager."}
                )

            department.manager = instance
            department.save()

        elif not new_manager_status and instance.department.manager == instance:
            instance.department.manager = None
            instance.department.save()

        instance.manager = new_manager_status
        instance.save()

        if role_data:
            if instance.user.role:
                instance.user.role.name = role_data.get("name", instance.user.role.name)
                instance.user.role.description = role_data.get(
                    "description", instance.user.role.description
                )
                instance.user.role.permissions = role_data.get(
                    "permissions", instance.user.role.permissions
                )
                instance.user.role.save()
            else:
                new_role = Role.objects.create(
                    name=role_data["name"],
                    description=role_data.get("description", ""),
                    permissions=role_data.get("permissions", []),
                )
                instance.user.role = new_role
                instance.user.save()

        return instance


class LeaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leave
        fields = "__all__"

    def update(self, instance, validated_data):
        instance.status = validated_data.get("status", instance.status)
        instance.save()
        return instance
