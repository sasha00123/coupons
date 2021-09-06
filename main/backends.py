from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password


class EmailAuthenticationBackend:
    def authenticate(self, username: str = None, password: str = None):
        try:
            user = get_user_model().objects.get(email=username)
        except get_user_model().DoesNotExist:
            return None
        if check_password(password, user.password):
            if user.atype == "C":
                user.set_unusable_password()
                user.save()
            return user
        return None

    def get_user(self, user_id: int):
        try:
            return get_user_model().objects.get(pk=user_id)
        except get_user_model().DoesNotExist:
            return None
