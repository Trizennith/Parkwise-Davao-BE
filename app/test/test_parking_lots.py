from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from app.api.parking_lots.models import ParkingLot, ParkingSpace
from app.api.accounts.models import User

class ParkingLotsAPITestCase(APITestCase):
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
        
        # Create test parking lot
        self.parking_lot = ParkingLot.objects.create(
            name='Test Parking Lot',
            address='123 Test St',
            latitude=10.123,
            longitude=123.456,
            total_spaces=10,
            available_spaces=10,
            hourly_rate=50.00
        )
        
        # Create API clients
        self.admin_client = APIClient()
        self.user_client = APIClient()
        self.anonymous_client = APIClient()
        
        # Authenticate clients
        self.admin_client.force_authenticate(user=self.admin_user)
        self.user_client.force_authenticate(user=self.regular_user)

    def test_parking_lot_list(self):
        """Test parking lot listing endpoint"""
        url = reverse('parkinglot-list')
        
        # Test authenticated user can view
        response = self.user_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Test anonymous user cannot view
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_parking_lot_create(self):
        """Test parking lot creation endpoint"""
        url = reverse('parkinglot-list')
        data = {
            'name': 'New Parking Lot',
            'address': '456 New St',
            'latitude': 11.123,
            'longitude': 124.456,
            'total_spaces': 20,
            'available_spaces': 20,
            'hourly_rate': 60.00
        }
        
        # Test admin can create
        response = self.admin_client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ParkingLot.objects.count(), 2)
        
        # Test regular user cannot create
        response = self.user_client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_parking_lot_update(self):
        """Test parking lot update endpoint"""
        url = reverse('parkinglot-detail', args=[self.parking_lot.id])
        data = {
            'name': 'Updated Parking Lot',
            'hourly_rate': 75.00
        }
        
        # Test admin can update
        response = self.admin_client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ParkingLot.objects.get(id=self.parking_lot.id).name, 'Updated Parking Lot')
        
        # Test regular user cannot update
        response = self.user_client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_parking_lot_delete(self):
        """Test parking lot deletion endpoint"""
        url = reverse('parkinglot-detail', args=[self.parking_lot.id])
        
        # Test admin can delete
        response = self.admin_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ParkingLot.objects.count(), 0)
        
        # Test regular user cannot delete
        self.parking_lot = ParkingLot.objects.create(
            name='Test Parking Lot 2',
            address='789 Test St',
            latitude=12.123,
            longitude=125.456,
            total_spaces=15,
            available_spaces=15,
            hourly_rate=55.00
        )
        url = reverse('parkinglot-detail', args=[self.parking_lot.id])
        response = self.user_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_parking_space_management(self):
        """Test parking space management endpoints"""
        # Test space listing
        url = reverse('parkingspace-list')
        response = self.user_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test space reservation
        space = ParkingSpace.objects.create(
            parking_lot=self.parking_lot,
            space_number='A001',
            status='available'
        )
        url = reverse('parkingspace-reserve', args=[space.id])
        response = self.user_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ParkingSpace.objects.get(id=space.id).status, 'reserved')
        
        # Test space occupation
        url = reverse('parkingspace-occupy', args=[space.id])
        response = self.user_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ParkingSpace.objects.get(id=space.id).status, 'occupied')
        
        # Test space vacation
        url = reverse('parkingspace-vacate', args=[space.id])
        response = self.user_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ParkingSpace.objects.get(id=space.id).status, 'available')

    def test_parking_lot_search(self):
        """Test parking lot search functionality"""
        url = reverse('parkinglot-list')
        
        # Test search by name
        response = self.user_client.get(f"{url}?search=Test")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Test search by address
        response = self.user_client.get(f"{url}?search=123")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Test search with no results
        response = self.user_client.get(f"{url}?search=Nonexistent")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0) 