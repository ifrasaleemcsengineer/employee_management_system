from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.utils import timezone

UserModel = get_user_model()


class CustomAuthenticationBackend(ModelBackend):

    def authenticate(self, request, email=None, username=None, password=None):
        if username:
            user = UserModel.objects.filter(username=username).first()
            if user and user.check_password(password) and user.is_active:
                user.last_login = timezone.now()
                user.save(update_fields=["last_login"])
                return user
        if email:
            user = UserModel.objects.filter(email=email).first()
            if user and user.check_password(password) and user.is_active:
                user.last_login = timezone.now()
                user.save(update_fields=["last_login"])
                return user
        return None
