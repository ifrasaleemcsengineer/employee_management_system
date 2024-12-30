from django.urls import path

from .views import *

urlpatterns = [
    # Employee URLs
    path(
        "",
        EmployeeViewSet.as_view({"post": "create", "get": "list", "delete": "destroy"}),
        name="manage-employees",
    ),
    path(
        "<int:pk>/",
        EmployeeViewSet.as_view(
            {"get": "retrieve", "put": "update", "patch": "partial_update"}
        ),
        name="employee-detail",
    ),
    # Leave URLs
    path(
        "leaves/",
        LeaveViewSet.as_view({"post": "create", "get": "list"}),
        name="manage-leaves",
    ),
    path(
        "leaves/<int:pk>/",
        LeaveViewSet.as_view(
            {"get": "retrieve", "put": "update", "patch": "partial_update"}
        ),
        name="leave-detail",
    ),
    # Role URLs
    path(
        "roles/",
        RoleViewSet.as_view({"post": "create", "get": "list"}),
        name="manage-roles",
    ),
    path(
        "roles/<int:pk>/",
        RoleViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="role-detail",
    ),
    # Salary URLs
    path(
        "salaries/",
        SalaryViewSet.as_view({"post": "create", "get": "list"}),
        name="manage-salaries",
    ),
    path(
        "salaries/<int:pk>/",
        SalaryViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="salary-detail",
    ),
]
