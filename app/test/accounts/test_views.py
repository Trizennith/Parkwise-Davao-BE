from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from app.api.accounts.models import Profile
from app.api.accounts.serializers import ProfileSerializer

User = get_user_model()

class UserRegistrationTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('user-register')
        self.valid_payload = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': '+1234567890'
        }

    def test_create_user_success(self):
        """Test successful user registration"""
        response = self.client.post(self.register_url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, 'test@example.com')

    def test_create_user_with_invalid_data(self):
        """Test user registration with invalid data"""
        invalid_payload = self.valid_payload.copy()
        invalid_payload['email'] = 'invalid-email'
        response = self.client.post(self.register_url, invalid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_with_existing_email(self):
        """Test user registration with existing email"""
        User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        response = self.client.post(self.register_url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class UserLoginTests(APITestCase):
    def setUp(self):
        self.login_url = reverse('token_obtain_pair')
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )

    def test_login_success(self):
        """Test successful user login"""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials"""
        payload = {
            'email': 'test@example.com',
            'password': 'wrongpass'
        }
        response = self.client.post(self.login_url, payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class ProfileTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.profile = Profile.objects.create(
            user=self.user,
            phone_number='+1234567890'
        )
        self.client.force_authenticate(user=self.user)
        self.profile_url = reverse('user-profile')

    def test_get_profile(self):
        """Test retrieving user profile"""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['email'], 'test@example.com')
        self.assertEqual(response.data['phone_number'], '+1234567890')

    def test_update_profile(self):
        """Test updating user profile"""
        payload = {
            'phone_number': '+0987654321',
            'address': '123 Test Street'
        }
        response = self.client.patch(self.profile_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['phone_number'], '+0987654321')
        self.assertEqual(response.data['address'], '123 Test Street')

    def test_update_profile_unauthorized(self):
        """Test updating profile without authentication"""
        self.client.force_authenticate(user=None)
        payload = {'phone_number': '+0987654321'}
        response = self.client.patch(self.profile_url, payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED) 