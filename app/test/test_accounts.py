from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from app.api.accounts.models import User, Profile
from django.contrib.auth import get_user_model

class AccountsAPITestCase(APITestCase):
    def setUp(self):
        # Create test users
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            username='admin',
            password='adminpass123',
            role=User.Role.ADMIN,
            is_staff=True
        )
        self.regular_user = User.objects.create_user(
            email='user@example.com',
            username='user',
            password='userpass123',
            role=User.Role.USER
        )
        
        # Create API clients
        self.admin_client = APIClient()
        self.user_client = APIClient()
        self.anonymous_client = APIClient()
        
        # Authenticate clients
        self.admin_client.force_authenticate(user=self.admin_user)
        self.user_client.force_authenticate(user=self.regular_user)

    def test_user_registration(self):
        """Test user registration endpoint"""
        url = reverse('user-registration')
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'newpass123',
            'password2': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        # Test successful registration
        response = self.anonymous_client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)
        
        # Test password mismatch
        data['password2'] = 'differentpass'
        response = self.anonymous_client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test restricted fields
        data['role'] = 'admin'
        data['password2'] = 'newpass123'
        response = self.anonymous_client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login(self):
        """Test user login endpoint"""
        url = reverse('user-login')
        data = {
            'email': 'user@example.com',
            'password': 'userpass123'
        }
        
        # Test successful login
        response = self.anonymous_client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        
        # Test invalid credentials
        data['password'] = 'wrongpass'
        response = self.anonymous_client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_profile(self):
        """Test user profile endpoints"""
        url = reverse('user-profile')
        
        # Test get profile
        response = self.user_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'user@example.com')
        
        # Test update profile
        data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        response = self.user_client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')

    def test_change_password(self):
        """Test password change endpoint"""
        url = reverse('change-password')
        data = {
            'old_password': 'userpass123',
            'new_password': 'newpass123',
            'new_password2': 'newpass123'
        }
        
        # Test successful password change
        response = self.user_client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test wrong old password
        data['old_password'] = 'wrongpass'
        response = self.user_client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_user_management(self):
        """Test admin user management endpoints"""
        # Test list users (admin only)
        url = reverse('user-list')
        response = self.admin_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test regular user cannot access
        response = self.user_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Test update user role (admin only)
        url = reverse('user-detail', args=[self.regular_user.id])
        data = {'role': 'admin'}
        response = self.admin_client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.get(id=self.regular_user.id).role, 'admin')
        
        # Test regular user cannot update role
        response = self.user_client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_deletion(self):
        """Test user deletion"""
        url = reverse('user-detail', args=[self.regular_user.id])
        
        # Test admin can delete user
        response = self.admin_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Test user cannot delete themselves
        url = reverse('user-detail', args=[self.admin_user.id])
        response = self.user_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) 