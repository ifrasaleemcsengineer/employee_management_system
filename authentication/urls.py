from django.urls import path

from .views import *

urlpatterns = [
    path(
        "users/",
        UserViewSet.as_view({"post": "create", "get": "list", "delete": "destroy"}),
        name="user-management",
    ),
    path(
        "users/<uuid:pk>/",
        UserViewSet.as_view(
            {"get": "retrieve", "put": "update", "patch": "partial_update"}
        ),
        name="user-detail",
    ),
    path("login/", LoginView.as_view(), name="login"),
    path("permissions/", PermissionListView.as_view(), name="permissions-list"),
]
