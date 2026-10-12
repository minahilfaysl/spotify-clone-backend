from django.test import override_settings
from rest_framework.test import APITestCase

from djangoapps.testing import make_user, User
from djangoapps.userdata.models import UserData

SIGNUP = {
    'email': 'new@example.com',
    'password': 'A-strong-pass-123',
    'password2': 'A-strong-pass-123',
    'profile_name': 'New User',
    'date_of_birth': '2000-01-01',
    'gender': 'F',
}


class SignupTests(APITestCase):
    def test_signup_creates_user_and_userdata(self):
        res = self.client.post('/api/users/signup/', SIGNUP, format='json')
        self.assertEqual(res.status_code, 201)
        user = User.objects.get(email='new@example.com')
        self.assertTrue(UserData.objects.filter(user=user).exists())
        self.assertIn('access', res.data['token'])

    def test_invalid_signup_returns_400_not_200(self):
        res = self.client.post('/api/users/signup/', {'email': 'bad'}, format='json')
        self.assertEqual(res.status_code, 400)
        self.assertIn('email', res.data)

    def test_password_mismatch_creates_nothing(self):
        res = self.client.post('/api/users/signup/', {**SIGNUP, 'password2': 'different'}, format='json')
        self.assertEqual(res.status_code, 400)
        self.assertFalse(User.objects.filter(email='new@example.com').exists())


class LoginAndRefreshTests(APITestCase):
    def setUp(self):
        self.user = make_user('alice')

    def test_login_with_email_and_refresh_token(self):
        res = self.client.post('/api/users/login/', {
            'username': 'alice@example.com', 'password': 'pw-for-tests-123'}, format='json')
        self.assertEqual(res.status_code, 200)
        refresh = res.data['token']['refresh']

        res = self.client.post('/api/users/token/refresh/', {'refresh': refresh}, format='json')
        self.assertEqual(res.status_code, 200)
        self.assertIn('access', res.data)

    def test_bad_token_is_401(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer not-a-token')
        self.assertEqual(self.client.get('/api/albums/').status_code, 401)


class AccountOwnershipTests(APITestCase):
    def setUp(self):
        self.alice = make_user('alice', is_artist=True)
        self.eve = make_user('eve')

    def test_cannot_change_someone_elses_artist_flag(self):
        self.client.force_authenticate(self.eve)
        res = self.client.put('/api/users/update_permission/alice/', {'is_artist': False}, format='json')
        self.assertEqual(res.status_code, 403)
        self.alice.refresh_from_db()
        self.assertTrue(self.alice.is_artist)

    def test_can_change_own_artist_flag(self):
        self.client.force_authenticate(self.eve)
        res = self.client.put('/api/users/update_permission/eve/', {'is_artist': True}, format='json')
        self.assertEqual(res.status_code, 200)
        self.eve.refresh_from_db()
        self.assertTrue(self.eve.is_artist)

    def test_cannot_edit_someone_elses_profile(self):
        self.client.force_authenticate(self.eve)
        res = self.client.put('/api/users/update_profile/alice/', {'profile_name': 'Hacked'}, format='json')
        self.assertEqual(res.status_code, 403)
        self.alice.refresh_from_db()
        self.assertEqual(self.alice.profile_name, 'Alice')

    def test_profiles_are_public(self):
        res = self.client.get('/api/users/user_profile/alice/')
        self.assertEqual(res.status_code, 200)


@override_settings(
    DEMO_READ_ONLY_USERS={'demo'},
    # admin pages need collected static files otherwise
    STORAGES={'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
              'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'}},
)
class DemoAccountTests(APITestCase):
    def setUp(self):
        self.demo = make_user('demo', is_artist=True, is_staff=True, is_superuser=True)
        self.admin = make_user('realadmin', is_staff=True, is_superuser=True)

    def test_demo_account_cannot_change_its_settings(self):
        self.client.force_authenticate(self.demo)
        res = self.client.put('/api/users/update_permission/demo/', {'is_artist': False}, format='json')
        self.assertEqual(res.status_code, 403)

    def test_demo_superuser_gets_no_admin_access(self):
        self.client.force_login(self.demo)
        self.assertEqual(self.client.get('/admin/').status_code, 302)  # sent to login

    def test_real_admin_still_has_admin_access(self):
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get('/admin/').status_code, 200)
