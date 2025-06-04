from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from app.api.parking_lots.models import ParkingLot, ParkingSpace
from app.api.reservations.models import Reservation
from app.api.reports.models import DailyReport, MonthlyReport, ParkingLotReport
from datetime import datetime, timedelta
from decimal import Decimal

User = get_user_model()

class ReportViewTests(APITestCase):
    def setUp(self):
        # Create users
        self.admin_user = User.objects.create_superuser(
            username='adminuser',
            email='admin@example.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User',
            role='admin'
        )
        self.user = User.objects.create_user(
            email='user@example.com',
            password='userpass123'
        )
        
        # Create parking lot and spaces
        self.parking_lot = ParkingLot.objects.create(
            name='Test Parking Lot',
            address='123 Test Street',
            total_spaces=50,
            hourly_rate=Decimal('10.00'),
            owner=self.admin_user
        )
        
        # Create parking spaces
        for i in range(5):
            ParkingSpace.objects.create(
                parking_lot=self.parking_lot,
                space_number=f'A{i+1}',
                space_type='standard'
        )
        
        # Create test reservations
        self.start_time = datetime.now() - timedelta(days=1)
        self.end_time = self.start_time + timedelta(hours=2)
        
        for i in range(3):
            space = ParkingSpace.objects.get(space_number=f'A{i+1}')
            Reservation.objects.create(
                user=self.user,
                parking_space=space,
                start_time=self.start_time,
                end_time=self.end_time,
                status='completed',
                payment=Decimal('20.00'),
                payment_time=self.start_time
            )
        
        # Set up URLs
        self.report_url = reverse('report-list')
        self.daily_report_url = reverse('report-daily')
        self.monthly_report_url = reverse('report-monthly')
        self.parking_lot_report_url = reverse('report-parking-lot', args=[self.parking_lot.id])

    def test_get_daily_report(self):
        """Test retrieving daily report"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.daily_report_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_revenue', response.data)
        self.assertIn('total_reservations', response.data)
        self.assertIn('occupancy_rate', response.data)

    def test_get_daily_report_unauthorized(self):
        """Test retrieving daily report without admin privileges"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.daily_report_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_monthly_report(self):
        """Test retrieving monthly report"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.monthly_report_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_revenue', response.data)
        self.assertIn('total_reservations', response.data)
        self.assertIn('average_occupancy_rate', response.data)

    def test_get_parking_lot_report(self):
        """Test retrieving parking lot specific report"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.parking_lot_report_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_revenue', response.data)
        self.assertIn('total_reservations', response.data)
        self.assertIn('occupancy_rate', response.data)

    def test_export_report(self):
        """Test exporting report data"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(
            reverse('report-export'),
            {'type': 'daily', 'start_date': '2024-01-01', 'end_date': '2024-12-31'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')

    def test_report_date_range(self):
        """Test retrieving report for specific date range"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(
            reverse('report-date-range'),
            {
                'start_date': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                'end_date': datetime.now().strftime('%Y-%m-%d')
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('reports', response.data)

    def test_report_summary(self):
        """Test retrieving report summary"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('report-summary'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_revenue', response.data)
        self.assertIn('total_reservations', response.data)
        self.assertIn('average_occupancy_rate', response.data)

    def test_report_validation(self):
        """Test report validation"""
        self.client.force_authenticate(user=self.admin_user)
        # Test invalid date range
        response = self.client.get(
            reverse('report-date-range'),
            {
                'start_date': '2024-12-31',
                'end_date': '2024-01-01'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test invalid report type
        response = self.client.get(
            reverse('report-export'),
            {'type': 'invalid', 'start_date': '2024-01-01', 'end_date': '2024-12-31'}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST) 