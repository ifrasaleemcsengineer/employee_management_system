from django.db.models import Q
from rest_framework import status
from rest_framework.viewsets import ModelViewSet

from employee_management_system.CustomResponse import CustomResponse
from employee_management_system.exceptions import custom_exception_handler
from employee_management_system.pagination import CustomPageNumberPagination
from permissions.permissions import *

from .models import Department
from .serializers import DepartmentSerializer


class DepartmentViewSet(ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [DynamicRolePermission]
    pagination_class = CustomPageNumberPagination

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
                status_code=status.HTTP_200_OK,
                message="Departments fetched successfully",
                data=serializer.data,
            )
        except Exception as e:
            return custom_exception_handler(e, None)

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return CustomResponse(
                status_code=status.HTTP_200_OK,
                message="Departments fetched successfully",
                data=serializer.data,
            )
        except Exception as e:
            return custom_exception_handler(e, None)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            department = serializer.save()
            return CustomResponse(
                status_code=status.HTTP_200_OK,
                message="Department created successfully",
                data=self.get_serializer(department).data,
            )
        except Exception as e:
            return custom_exception_handler(e, None)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return CustomResponse(
                status_code=status.HTTP_200_OK,
                message="Department retrieved successfully",
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
            self.perform_update(serializer)
            return CustomResponse(
                status_code=status.HTTP_200_OK,
                message="Department updated successfully",
                data=serializer.data,
            )
        except Exception as e:
            return custom_exception_handler(e, None)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return CustomResponse(
                status_code=status.HTTP_200_OK,
                message="Department deleted successfully",
                data={},
            )
        except Exception as e:
            return custom_exception_handler(e, None)
