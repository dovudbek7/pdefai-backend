from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


class EmailBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, username=None, **kwargs):
        # Django admin passes username=; API passes email=
        lookup = email or username
        if not lookup:
            return None
        try:
            user = User.objects.get(username=lookup)
        except User.DoesNotExist:
            return None
        if user.check_password(password):
            return user
        return None
