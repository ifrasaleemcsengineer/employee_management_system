from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.viewsets import ModelViewSet

from employee_management_system.CustomResponse import CustomResponse
from employee_management_system.exceptions import custom_exception_handler
from employee_management_system.pagination import CustomPageNumberPagination
from permissions.permissions import *

from .models import Employee, Leave, Role, Salary
from .serializers import (EmployeeSerializer, LeaveSerializer, RoleSerializer,
                          SalarySerializer)


class EmployeeViewSet(ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [DynamicRolePermission]
    pagination_class = CustomPageNumberPagination

    def format_validation_errors(self, exc):
        error_messages = []

        def extract_errors(errors, parent_key=""):
            if isinstance(errors, dict):
                for field, field_errors in errors.items():
                    new_key = f"{parent_key}{field}." if parent_key else field
                    extract_errors(field_errors, parent_key=new_key)
            elif isinstance(errors, list):
                for error in errors:
                    if isinstance(error, dict):
                        extract_errors(error, parent_key=parent_key)
                    else:
                        error_messages.append(str(error))
            else:
                error_messages.append(str(errors))

        extract_errors(exc.detail)
        return " ".join(error_messages)

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get("q", None)
        department_id = self.request.query_params.get("department_id", None)

        if search_query:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search_query)
                | Q(user__last_name__icontains=search_query)
                | Q(user__email__icontains=search_query)
                | Q(user__username__icontains=search_query)
                | Q(department__name__icontains=search_query)
            )
        if department_id:
            queryset = queryset.filter(department_id=department_id)

        return queryset.order_by("id")

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return CustomResponse(
                status_code=status.HTTP_200_OK,
                message="Employees fetched successfully.",
                data=serializer.data,
            )
        except Exception as e:
            return custom_exception_handler(e, None)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            employee = serializer.save()
            response_serializer = EmployeeSerializer(employee)
            return CustomResponse(
                status_code=status.HTTP_200_OK,
                message="Employee created successfully.",
                data=response_serializer.data,
            )
        except ValidationError as e:
            error_message = self.format_validation_errors(e)
            return CustomResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                message=error_message,
                data={},
            )
        except Exception as e:
            return custom_exception_handler(e, None)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return CustomResponse(
                status_code=status.HTTP_200_OK,
                message="Employee retrieved successfully",
                data=serializer.data,
            )
        except Exception as e:
            return custom_exception_handler(e, None)

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop("partial", False)
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            employee = serializer.save()
            return CustomResponse(
                status_code=status.HTTP_200_OK,
                message="Employee updated successfully.",
                data=self.get_serializer(employee).data,
            )
        except ValidationError as e:
            error_message = self.format_validation_errors(e)
            return CustomResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                message=error_message,
                data={},
            )
        except Exception as e:
            return custom_exception_handler(e, None)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return CustomResponse(
                status_code=status.HTTP_200_OK,
                message="Employee deleted successfully",
                data={},
            )
        except Exception as e:
            return custom_exception_handler(e, None)


class LeaveViewSet(ModelViewSet):
    queryset = Leave.objects.all()
    serializer_class = LeaveSerializer
    permission_classes = [DynamicRolePermission]

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get("q", None)
        employee_id = self.request.query_params.get("employee_id", None)

        if search_query:
            queryset = queryset.filter(
                Q(reason__icontains=search_query)
                | Q(employee__user__first_name__icontains=search_query)
                | Q(employee__user__last_name__icontains=search_query)
            )
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)

        return queryset.order_by("id")

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return CustomResponse(
                status_code=status.HTTP_200_OK,
                message="Leave retrieved successfully",
                data=serializer.data,
            )
        except Exception as e:
            return custom_exception_handler(e, None)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            leave_request = serializer.save()
            response_serializer = self.get_serializer(leave_request)
            return CustomResponse(
                status_code=status.HTTP_200_OK,
                message="Leave request created successfully.",
                data=response_serializer.data,
            )
        except ValidationError as e:
            error_message = "; ".join(
                [str(error) for errors in e.detail.values() for error in errors]
            )
            return CustomResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                message=error_message,
                data={},
            )
        except Exception as e:
            return custom_exception_handler(e, None)

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return CustomResponse(
                status_code=status.HTTP_200_OK,
                message="Leave requests fetched successfully.",
                data=serializer.data,
            )
        except Exception as e:
            return custom_exception_handler(e, None)

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return CustomResponse(
                status_code=status.HTTP_200_OK,
                message="Leave request updated successfully",
                data=serializer.data,
            )
        except ValidationError as e:
            error_message = "; ".join(
                [str(error) for errors in e.detail.values() for error in errors]
            )
            return CustomResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                message=error_message,
                data={},
            )
        except Exception as e:
            return custom_exception_handler(e, None)


class RoleViewSet(ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [DynamicRolePermission]

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get("q", None)

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | Q(description__icontains=search_query)
            )
        return queryset.order_by("id")

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return CustomResponse(
                status.HTTP_200_OK, "Roles fetched successfully", serializer.data
            )
        except Exception as e:
            return custom_exception_handler(e, None)


class SalaryViewSet(ModelViewSet):
    queryset = Salary.objects.all()
    serializer_class = SalarySerializer
    permission_classes = [DynamicRolePermission]
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get("q", None)
        employee_id = self.request.query_params.get("employee_id", None)

        if search_query:
            queryset = queryset.filter(
                Q(pay_rate__icontains=search_query)
                | Q(start_date__icontains=search_query)
                | Q(end_date__icontains=search_query)
                | Q(pay_period__icontains=search_query)
            )
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)

        return queryset.order_by("-start_date")

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return CustomResponse(
                status_code=status.HTTP_200_OK,
                message="Salaries fetched successfully.",
                data=serializer.data,
            )
        except Exception as e:
            return custom_exception_handler(e, None)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            salary = serializer.save()
            response_serializer = self.get_serializer(salary)
            return CustomResponse(
                status_code=status.HTTP_200_OK,
                message="Salary record created successfully.",
                data=response_serializer.data,
            )
        except ValidationError as e:
            error_message = "; ".join(
                [str(error) for errors in e.detail.values() for error in errors]
            )
            return CustomResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                message=error_message,
                data={},
            )
        except Exception as e:
            return custom_exception_handler(e, None)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return CustomResponse(
                status_code=status.HTTP_200_OK,
                message="Salary record retrieved successfully.",
                data=serializer.data,
            )
        except Exception as e:
            return custom_exception_handler(e, None)

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop("partial", False)
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            salary = serializer.save()
            response_serializer = self.get_serializer(salary)
            return CustomResponse(
                status_code=status.HTTP_200_OK,
                message="Salary record updated successfully.",
                data=response_serializer.data,
            )
        except ValidationError as e:
            error_message = "; ".join(
                [str(error) for errors in e.detail.values() for error in errors]
            )
            return CustomResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                message=error_message,
                data={},
            )
        except Exception as e:
            return custom_exception_handler(e, None)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return CustomResponse(
                status_code=status.HTTP_200_OK,
                message="Salary record deleted successfully.",
                data={},
            )
        except Exception as e:
            return custom_exception_handler(e, None)
