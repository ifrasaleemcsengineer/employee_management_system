# serializers.py
import re

from django.db import IntegrityError
from rest_framework import serializers

from employees.models import Role

from .models import User


class UserSerializer(serializers.ModelSerializer):
    role = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(), required=False, allow_null=True
    )
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            "is_admin",
            "role",
            "is_active",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }

    def validate_password(self, value):
        password = value
        if len(password) < 8:
            raise serializers.ValidationError(
                "Password must be at least 8 characters long."
            )
        if not re.search("[A-Z]", password):
            raise serializers.ValidationError(
                "Password must contain at least one uppercase letter."
            )
        if not re.search("[a-z]", password):
            raise serializers.ValidationError(
                "Password must contain at least one lowercase letter."
            )
        if not re.search("[0-9]", password):
            raise serializers.ValidationError(
                "Password must contain at least one number."
            )
        if not re.search('[!@#$%^&*(),.?":{}|<>]', password):
            raise serializers.ValidationError(
                "Password must contain at least one special character."
            )
        return password

    def validate_username(self, value):
        if (
            User.objects.filter(username=value)
            .exclude(pk=self.instance.pk if self.instance else None)
            .exists()
        ):
            raise serializers.ValidationError(
                "A user with this username already exists."
            )
        return value

    def validate_email(self, value):
        if (
            User.objects.filter(email=value)
            .exclude(pk=self.instance.pk if self.instance else None)
            .exists()
        ):
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_is_admin(self, value):
        if value and User.objects.filter(is_admin=True).exists():
            if not self.instance or not self.instance.is_admin:
                raise serializers.ValidationError("An admin user already exists.")
        return value

    def create(self, validated_data):
        validated_data["is_admin"] = self.validate_is_admin(
            validated_data.get("is_admin", False)
        )
        role = validated_data.pop("role", None)
        password = validated_data.pop("password", None)

        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
        user.role = role
        user.save()
        return user

    def update(self, instance, validated_data):
        is_admin = validated_data.get("is_admin", instance.is_admin)
        if is_admin != instance.is_admin:
            validated_data["is_admin"] = self.validate_is_admin(is_admin)

        role = validated_data.pop("role", None)
        password = validated_data.pop("password", None)

        instance.username = validated_data.get("username", instance.username)
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.email = validated_data.get("email", instance.email)
        instance.is_admin = validated_data.get("is_admin", instance.is_admin)

        if role:
            instance.role = role

        if password:
            instance.set_password(password)

        try:
            instance.save()
        except IntegrityError as e:
            raise serializers.ValidationError({"detail": str(e)})

        return instance


class LoginSerializer(serializers.Serializer):
    email_or_username = serializers.CharField()
    password = serializers.CharField(write_only=True)
