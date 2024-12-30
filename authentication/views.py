from django.contrib.auth import authenticate
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView

from employee_management_system.CustomResponse import CustomResponse
from employee_management_system.exceptions import custom_exception_handler
from employees.models import CUSTOM_PERMISSIONS
from permissions.permissions import CustomUserPermission

from .models import User
from .serializers import LoginSerializer, UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [CustomUserPermission]

    def create(self, request, *args, **kwargs):
        is_admin = request.data.get("is_admin", False)
        if is_admin and User.objects.filter(is_admin=True).exists():
            return CustomResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="An admin user already exists.",
                data={},
            )
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            return CustomResponse(
                status_code=status.HTTP_200_OK,
                message="User created successfully.",
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
            user = serializer.save()
            return CustomResponse(
                status_code=status.HTTP_200_OK,
                message="User updated successfully.",
                data=serializer.data,
            )

        except Exception as e:
            return custom_exception_handler(e, None)

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return CustomResponse(
                status_code=status.HTTP_200_OK,
                message="Users fetched successfully.",
                data=serializer.data,
            )
        except Exception as e:
            return custom_exception_handler(e, None)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return CustomResponse(
                status_code=status.HTTP_200_OK,
                message="User retrieved successfully.",
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
                message="User deleted successfully.",
                data={},
            )
        except Exception as e:
            return custom_exception_handler(e, None)


class LoginView(APIView):
    def post(self, request, format="json"):
        try:
            serializer = LoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            email_or_username = serializer.validated_data.get("email_or_username")
            password = serializer.validated_data.get("password")

            user = authenticate(request, username=email_or_username, password=password)

            if not user:
                return CustomResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message="Invalid Credentials.",
                    data={},
                )

            token, _ = Token.objects.get_or_create(user=user)

            return CustomResponse(
                status_code=status.HTTP_200_OK,
                message="User logged in successfully.",
                data={"token": token.key, "user": UserSerializer(user).data},
            )
        except ValidationError as e:
            error_message = "; ".join(
                [f"{field}: {', '.join(errors)}" for field, errors in e.detail.items()]
            )
            return CustomResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                message=f"Validation Error: {error_message}",
                data={},
            )
        except Exception as e:
            return custom_exception_handler(e, None)


class PermissionListView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            custom_permissions_names = list(CUSTOM_PERMISSIONS.values())

            return CustomResponse(
                status_code=status.HTTP_200_OK,
                message="Custom permissions fetched successfully.",
                data=custom_permissions_names,
            )
        except Exception as e:
            return custom_exception_handler(e, None)
