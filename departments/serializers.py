from rest_framework import serializers

from .models import Department


class DepartmentSerializer(serializers.ModelSerializer):
    manager = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ["id", "name", "manager", "description"]

    def get_manager(self, obj):
        if obj.manager:
            return {
                "id": obj.manager.id,
                "user": {
                    "id": obj.manager.id,
                    "username": obj.manager.username,
                    "first_name": obj.manager.first_name,
                    "last_name": obj.manager.last_name,
                },
            }
        return None

    def validate_name(self, value):
        instance = self.instance

        if instance and instance.name.lower() == value.lower():
            return value

        if Department.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError(
                "A department with this name already exists."
            )

        return value
