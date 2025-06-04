from django.test import TestCase
from django.contrib.auth import get_user_model
from app.api.parking_lots.models import ParkingLot, ParkingSpace
from app.api.reservations.models import Reservation
from datetime import datetime, timedelta
from decimal import Decimal

User = get_user_model()

class ReservationModelTests(TestCase):
    def setUp(self):
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
            latitude=7.123456,
            longitude=125.654321,
            total_spaces=50,
            available_spaces=50,
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

    def test_reservation_creation(self):
        """Test reservation creation"""
        reservation = Reservation.objects.create(
            user=self.user,
            parking_lot=self.parking_lot,
            parking_space=self.parking_space,
            vehicle_plate='ABC123',
            start_time=self.start_time,
            end_time=self.end_time
        )
        
        self.assertEqual(reservation.user, self.user)
        self.assertEqual(reservation.parking_lot, self.parking_lot)
        self.assertEqual(reservation.parking_space, self.parking_space)
        self.assertEqual(reservation.vehicle_plate, 'ABC123')
        self.assertEqual(reservation.start_time, self.start_time)
        self.assertEqual(reservation.end_time, self.end_time)
        self.assertEqual(reservation.status, Reservation.Status.ACTIVE)

    def test_reservation_str(self):
        """Test reservation string representation"""
        reservation = Reservation.objects.create(
            user=self.user,
            parking_lot=self.parking_lot,
            parking_space=self.parking_space,
            vehicle_plate='ABC123',
            start_time=self.start_time,
            end_time=self.end_time
        )
        
        expected_str = f"Reservation {reservation.id} - {self.user.get_full_name()}"
        self.assertEqual(str(reservation), expected_str)

    def test_reservation_duration(self):
        """Test reservation duration calculation"""
        reservation = Reservation.objects.create(
            user=self.user,
            parking_lot=self.parking_lot,
            parking_space=self.parking_space,
            vehicle_plate='ABC123',
            start_time=self.start_time,
            end_time=self.end_time
        )
        
        expected_duration = Decimal('2.0')  # 2 hours
        self.assertEqual(reservation.duration, expected_duration)

    def test_reservation_total_cost(self):
        """Test reservation total cost calculation"""
        reservation = Reservation.objects.create(
            user=self.user,
            parking_lot=self.parking_lot,
            parking_space=self.parking_space,
            vehicle_plate='ABC123',
            start_time=self.start_time,
            end_time=self.end_time
        )
        
        expected_cost = Decimal('20.00')  # 2 hours * $10.00/hour
        self.assertEqual(reservation.total_cost, expected_cost)

    def test_reservation_status_transitions(self):
        """Test reservation status transitions"""
        reservation = Reservation.objects.create(
            user=self.user,
            parking_lot=self.parking_lot,
            parking_space=self.parking_space,
            vehicle_plate='ABC123',
            start_time=self.start_time,
            end_time=self.end_time
        )
        
        # Test valid transitions
        reservation.status = Reservation.Status.COMPLETED
        reservation.save()
        self.assertEqual(reservation.status, Reservation.Status.COMPLETED)
        
        # Test invalid transition
        with self.assertRaises(Exception):
            reservation.status = 'invalid_status'
            reservation.save()

    def test_reservation_validation(self):
        """Test reservation validation"""
        # Test end time before start time
        with self.assertRaises(Exception):
            Reservation.objects.create(
                user=self.user,
                parking_lot=self.parking_lot,
                parking_space=self.parking_space,
                vehicle_plate='ABC123',
                start_time=self.end_time,
                end_time=self.start_time
            )
        
        # Test reservation in the past
        past_time = datetime.now() - timedelta(hours=1)
        with self.assertRaises(Exception):
            Reservation.objects.create(
                user=self.user,
                parking_lot=self.parking_lot,
                parking_space=self.parking_space,
                vehicle_plate='ABC123',
                start_time=past_time,
                end_time=past_time + timedelta(hours=1)
            )

    def test_reservation_cancellation(self):
        """Test reservation cancellation"""
        reservation = Reservation.objects.create(
            user=self.user,
            parking_space=self.parking_space,
            start_time=self.start_time,
            end_time=self.end_time
        )
        
        reservation.cancel()
        self.assertEqual(reservation.status, 'cancelled')
        self.assertIsNotNone(reservation.cancelled_at)

    def test_reservation_completion(self):
        """Test reservation completion"""
        reservation = Reservation.objects.create(
            user=self.user,
            parking_space=self.parking_space,
            start_time=self.start_time,
            end_time=self.end_time,
            status='paid'
        )
        
        reservation.complete()
        self.assertEqual(reservation.status, 'completed')
        self.assertIsNotNone(reservation.completed_at) 