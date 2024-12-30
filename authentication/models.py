import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now
from rest_framework.authtoken.models import Token

from employees.models import Role


class User(AbstractUser):
    id = models.UUIDField(
        default=uuid.uuid4, unique=True, editable=False, db_index=True, primary_key=True
    )
    email = models.EmailField(max_length=254, blank=True, null=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)
    role = models.ForeignKey(
        Role, on_delete=models.CASCADE, null=True, blank=True, related_name="users"
    )
    first_name = models.CharField(max_length=40, null=True, blank=True)
    last_name = models.CharField(max_length=40, null=True, blank=True)

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="custom_user_set",
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )

    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="custom_user_permissions_set",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

    REQUIRED_FIELDS = ["email"]
    USERNAME_FIELD = "username"

    @property
    def tokens(self):
        try:
            if not self.pk:
                return None
            token, _ = Token.objects.get_or_create(user=self)
            return token.key
        except Exception as e:
            return None

    def save(self, *args, **kwargs):
        if self.is_admin:
            self.is_superuser = True
            self.is_staff = True
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
