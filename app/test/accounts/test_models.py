from django.test import TestCase
from django.contrib.auth import get_user_model
from app.api.accounts.models import Profile
from app.api.accounts.serializers import UserProfileSerializer

User = get_user_model()

class UserModelTests(TestCase):
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_create_user(self):
        """Test user creation"""
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.first_name, 'Test')
        self.assertEqual(self.user.last_name, 'User')
        self.assertTrue(self.user.check_password('testpass123'))
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)

    def test_create_superuser(self):
        """Test superuser creation"""
        admin_user = User.objects.create_superuser(
            email='admin@example.com',
            username='adminuser',
            password='adminpass123'
        )
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_user_str(self):
        """Test user string representation"""
        self.assertEqual(str(self.user), 'Test User (test@example.com)')

class ProfileModelTests(TestCase):
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

    def test_profile_creation(self):
        """Test user profile creation"""
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.phone_number, '+1234567890')
        self.assertTrue(isinstance(self.profile, Profile))
        self.assertEqual(str(self.profile), 'test@example.com')

    def test_profile_serializer(self):
        """Test user profile serializer"""
        serializer = UserProfileSerializer(self.profile)
        self.assertEqual(serializer.data['phone_number'], '+1234567890')
        self.assertEqual(serializer.data['user']['email'], 'test@example.com')

    def test_profile_update(self):
        """Test user profile update"""
        self.profile.phone_number = '+0987654321'
        self.profile.save()
        self.assertEqual(self.profile.phone_number, '+0987654321')

    def test_profile_delete(self):
        """Test user profile deletion"""
        profile_id = self.profile.id
        self.profile.delete()
        self.assertFalse(Profile.objects.filter(id=profile_id).exists()) 