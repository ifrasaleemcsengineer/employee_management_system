from django.urls import path

from .views import *

urlpatterns = [
    path(
        "",
        DepartmentViewSet.as_view(
            {"post": "create", "get": "list", "delete": "destroy"}
        ),
        name="manage-departments",
    ),
    path(
        "<int:pk>/",
        DepartmentViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="department-detail",
    ),
]
