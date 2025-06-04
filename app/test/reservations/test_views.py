from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from app.api.parking_lots.models import ParkingLot, ParkingSpace
from app.api.reservations.models import Reservation
from datetime import datetime, timedelta
from decimal import Decimal

User = get_user_model()

class ReservationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create users
        self.user = User.objects.create_user(
            email='user@example.com',
            username='regularuser',
            password='userpass123'
        )
        self.owner = User.objects.create_user(
            email='owner@example.com',
            username='owneruser',
            password='ownerpass123'
        )
        
        # Create parking lot and space
        self.parking_lot = ParkingLot.objects.create(
            name='Test Parking Lot',
            address='123 Test Street',
            latitude=72.123456,
            longitude=15.654321,
            total_spaces=50,
            hourly_rate=Decimal('10.00'),
            owner=self.owner
        )
        self.parking_space = ParkingSpace.objects.create(
            parking_lot=self.parking_lot,
            space_number='A1',
            space_type='standard'
        )
        
        # Set up test times
        self.start_time = datetime.now() + timedelta(hours=1)
        self.end_time = self.start_time + timedelta(hours=2)
        
        # Set up test data
        self.valid_payload = {
            'parking_space': self.parking_space.id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat()
        }
        
        # URLs
        self.list_url = reverse('reservation-list')
        self.detail_url = lambda id: reverse('reservation-detail', args=[id])

    def test_create_reservation_unauthorized(self):
        """Test creating reservation without authentication"""
        response = self.client.post(self.list_url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_reservation_success(self):
        """Test successful reservation creation"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.list_url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Reservation.objects.count(), 1)
        self.assertEqual(Reservation.objects.get().user, self.user)

    def test_create_reservation_invalid_time(self):
        """Test reservation creation with invalid time"""
        self.client.force_authenticate(user=self.user)
        
        # End time before start time
        invalid_payload = self.valid_payload.copy()
        invalid_payload['end_time'] = (self.start_time - timedelta(hours=1)).isoformat()
        
        response = self.client.post(self.list_url, invalid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_reservations(self):
        """Test listing user's reservations"""
        self.client.force_authenticate(user=self.user)
        
        # Create some reservations
        Reservation.objects.create(
            user=self.user,
            parking_space=self.parking_space,
            start_time=self.start_time,
            end_time=self.end_time
        )
        
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_reservation(self):
        """Test retrieving a specific reservation"""
        self.client.force_authenticate(user=self.user)
        
        # Create a reservation
        reservation = Reservation.objects.create(
            user=self.user,
            parking_space=self.parking_space,
            start_time=self.start_time,
            end_time=self.end_time
        )
        
        response = self.client.get(self.detail_url(reservation.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], reservation.id)

    def test_update_reservation(self):
        """Test updating a reservation"""
        self.client.force_authenticate(user=self.user)
        
        # Create a reservation
        reservation = Reservation.objects.create(
            user=self.user,
            parking_space=self.parking_space,
            start_time=self.start_time,
            end_time=self.end_time
        )
        
        # Update payload
        new_end_time = self.end_time + timedelta(hours=1)
        update_payload = {
            'end_time': new_end_time.isoformat()
        }
        
        response = self.client.patch(self.detail_url(reservation.id), update_payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reservation.refresh_from_db()
        self.assertEqual(reservation.end_time, new_end_time)

    def test_cancel_reservation(self):
        """Test canceling a reservation"""
        self.client.force_authenticate(user=self.user)
        
        # Create a reservation
        reservation = Reservation.objects.create(
            user=self.user,
            parking_space=self.parking_space,
            start_time=self.start_time,
            end_time=self.end_time
        )
        
        response = self.client.post(f"{self.detail_url(reservation.id)}cancel/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reservation.refresh_from_db()
        self.assertEqual(reservation.status, 'cancelled')

    def test_reservation_validation(self):
        """Test reservation validation rules"""
        self.client.force_authenticate(user=self.user)
        
        # Test overlapping reservations
        Reservation.objects.create(
            user=self.user,
            parking_space=self.parking_space,
            start_time=self.start_time,
            end_time=self.end_time
        )
        
        # Try to create overlapping reservation
        overlapping_payload = self.valid_payload.copy()
        response = self.client.post(self.list_url, overlapping_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reservation_payment(self):
        """Test reservation payment process"""
        self.client.force_authenticate(user=self.user)
        # Create a reservation
        reservation = Reservation.objects.create(
            user=self.user,
            parking_space=self.parking_space,
            start_time=self.start_time,
            end_time=self.end_time,
            status='confirmed'
        )
        
        payload = {
            'payment_method': 'credit_card',
            'amount': '20.00'
        }
        response = self.client.post(
            reverse('reservation-payment', args=[reservation.id]),
            payload
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Reservation.objects.get(id=reservation.id).status,
            'paid'
        ) 