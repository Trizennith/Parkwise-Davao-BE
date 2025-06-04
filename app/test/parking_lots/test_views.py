from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from app.api.parking_lots.models import ParkingLot, ParkingSpace
from app.api.accounts.models import Profile

User = get_user_model()

class ParkingLotTests(APITestCase):
    def setUp(self):
        # Create admin user
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            username='adminuser',
            password='adminpass123'
        )
        self.admin_profile = Profile.objects.create(
            user=self.admin_user,
            phone_number='+1234567890'
        )
        
        # Create regular user
        self.user = User.objects.create_user(
            email='user@example.com',
            username='regularuser',
            password='userpass123'
        )
        self.user_profile = Profile.objects.create(
            user=self.user,
            phone_number='+0987654321'
        )
        
        # Create test parking lot
        self.parking_lot = ParkingLot.objects.create(
            name='Test Parking Lot',
            address='123 Test Street',
            latitude=7.123456,
            longitude=125.654321,
            total_spaces=50,
            available_spaces=50,
            hourly_rate=10.00,
            owner=self.admin_user
        )
        
        # Create test parking spaces
        for i in range(5):
            ParkingSpace.objects.create(
                parking_lot=self.parking_lot,
                space_number=f'A{i+1}',
                space_type='standard'
            )
        
        self.parking_lot_url = reverse('parking-lot-list')
        self.parking_lot_detail_url = reverse('parking-lot-detail', args=[self.parking_lot.id])

    def test_create_parking_lot(self):
        """Test creating a new parking lot"""
        self.client.force_authenticate(user=self.admin_user)
        payload = {
            'name': 'New Parking Lot',
            'address': '456 New Street',
            'total_spaces': 30,
            'hourly_rate': 15.00
        }
        response = self.client.post(self.parking_lot_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ParkingLot.objects.count(), 2)
        self.assertEqual(response.data['name'], 'New Parking Lot')

    def test_create_parking_lot_unauthorized(self):
        """Test creating parking lot without admin privileges"""
        self.client.force_authenticate(user=self.user)
        payload = {
            'name': 'New Parking Lot',
            'address': '456 New Street',
            'total_spaces': 30,
            'hourly_rate': 15.00
        }
        response = self.client.post(self.parking_lot_url, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_parking_lots(self):
        """Test listing all parking lots"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.parking_lot_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_parking_lot_detail(self):
        """Test retrieving parking lot details"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.parking_lot_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Parking Lot')
        self.assertEqual(response.data['total_spaces'], 50)

    def test_update_parking_lot(self):
        """Test updating parking lot details"""
        self.client.force_authenticate(user=self.admin_user)
        payload = {
            'name': 'Updated Parking Lot',
            'hourly_rate': 20.00
        }
        response = self.client.patch(self.parking_lot_detail_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Parking Lot')
        self.assertEqual(float(response.data['hourly_rate']), 20.00)

    def test_delete_parking_lot(self):
        """Test deleting a parking lot"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.parking_lot_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ParkingLot.objects.count(), 0)

class ParkingSpaceTests(APITestCase):
    def setUp(self):
        # Create admin user
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            username='adminuser',
            password='adminpass123'
        )
        
        # Create parking lot
        self.parking_lot = ParkingLot.objects.create(
            name='Test Parking Lot',
            address='123 Test Street',
            latitude=7.123456,
            longitude=125.654321,
            total_spaces=50,
            available_spaces=50,
            hourly_rate=10.00,
            owner=self.admin_user
        )
        
        # Create parking space
        self.parking_space = ParkingSpace.objects.create(
            parking_lot=self.parking_lot,
            space_number='A1',
            space_type='standard'
        )
        
        self.space_url = reverse('parking-space-list')
        self.space_detail_url = reverse('parking-space-detail', args=[self.parking_space.id])

    def test_create_parking_space(self):
        """Test creating a new parking space"""
        self.client.force_authenticate(user=self.admin_user)
        payload = {
            'parking_lot': self.parking_lot.id,
            'space_number': 'A2',
            'space_type': 'handicap'
        }
        response = self.client.post(self.space_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ParkingSpace.objects.count(), 2)

    def test_list_parking_spaces(self):
        """Test listing all parking spaces"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.space_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_parking_space(self):
        """Test updating parking space details"""
        self.client.force_authenticate(user=self.admin_user)
        payload = {
            'space_type': 'handicap',
            'is_available': False
        }
        response = self.client.patch(self.space_detail_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['space_type'], 'handicap')
        self.assertFalse(response.data['is_available'])

    def test_delete_parking_space(self):
        """Test deleting a parking space"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.space_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ParkingSpace.objects.count(), 0) 