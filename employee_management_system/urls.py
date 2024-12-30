from django.urls import include, path

urlpatterns = [
    path("auth/", include("authentication.urls")),
    path("employees/", include("employees.urls")),
    path("departments/", include("departments.urls")),
]
