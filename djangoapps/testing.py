"""Small helpers shared by the app test suites."""
from django.contrib.auth import get_user_model

from djangoapps.userdata.models import UserData

User = get_user_model()


def make_user(username, is_artist=False, **extra):
    user = User.objects.create_user(
        username=username,
        email=f'{username}@example.com',
        password='pw-for-tests-123',
        profile_name=username.title(),
        date_of_birth='2000-01-01',
        is_artist=is_artist,
        **extra,
    )
    UserData.objects.create(user=user)
    return user
