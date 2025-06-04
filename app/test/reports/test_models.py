from django.test import TestCase
from django.contrib.auth import get_user_model
from app.api.parking_lots.models import ParkingLot
from app.api.reports.models import DailyReport, MonthlyReport, ParkingLotReport
from datetime import datetime, timedelta
from decimal import Decimal
from django.core.exceptions import ValidationError

User = get_user_model()

class DailyReportModelTests(TestCase):
    def setUp(self):
        self.date = datetime.now().date()
        self.daily_report = DailyReport.objects.create(
            date=self.date,
            total_revenue=Decimal('1000.00'),
            total_reservations=50,
            average_duration=2.5,
            peak_hour=datetime.now().time(),
            occupancy_rate=75.5
        )

    def test_daily_report_creation(self):
        """Test daily report creation"""
        self.assertEqual(self.daily_report.date, self.date)
        self.assertEqual(self.daily_report.total_revenue, Decimal('1000.00'))
        self.assertEqual(self.daily_report.total_reservations, 50)
        self.assertEqual(self.daily_report.average_duration, 2.5)
        self.assertEqual(self.daily_report.occupancy_rate, 75.5)

    def test_daily_report_str(self):
        """Test daily report string representation"""
        expected_str = f"Daily Report - {self.date}"
        self.assertEqual(str(self.daily_report), expected_str)

    def test_daily_report_update(self):
        """Test daily report update"""
        self.daily_report.total_revenue = Decimal('1500.00')
        self.daily_report.total_reservations = 75
        self.daily_report.save()
        
        updated_report = DailyReport.objects.get(id=self.daily_report.id)
        self.assertEqual(updated_report.total_revenue, Decimal('1500.00'))
        self.assertEqual(updated_report.total_reservations, 75)

    def test_daily_report_validation(self):
        """Test daily report validation"""
        # Test duplicate date
        with self.assertRaises(Exception):
            DailyReport.objects.create(
                date=self.date,
                total_revenue=Decimal('500.00'),
                total_reservations=25
            )

    def test_generate_report_empty_data(self):
        """Test generating report with no reservations"""
        test_date = datetime.now().date() + timedelta(days=1)  # Use future date to ensure no data
        report = DailyReport.generate_report(date=test_date)
        
        self.assertEqual(report.date, test_date)
        self.assertEqual(report.total_revenue, Decimal('0.00'))
        self.assertEqual(report.total_reservations, 0)
        self.assertEqual(report.average_duration, 0)
        self.assertEqual(report.occupancy_rate, 0)
        self.assertIsNone(report.peak_hour)

class MonthlyReportModelTests(TestCase):
    def setUp(self):
        self.year = 2024
        self.month = 1
        self.monthly_report = MonthlyReport.objects.create(
            year=self.year,
            month=self.month,
            total_revenue=Decimal('30000.00'),
            total_reservations=1500,
            average_duration=2.0,
            average_occupancy_rate=80.0,
            peak_day=datetime.now().date()
        )

    def test_monthly_report_creation(self):
        """Test monthly report creation"""
        self.assertEqual(self.monthly_report.year, self.year)
        self.assertEqual(self.monthly_report.month, self.month)
        self.assertEqual(self.monthly_report.total_revenue, Decimal('30000.00'))
        self.assertEqual(self.monthly_report.total_reservations, 1500)
        self.assertEqual(self.monthly_report.average_duration, 2.0)
        self.assertEqual(self.monthly_report.average_occupancy_rate, 80.0)

    def test_monthly_report_str(self):
        """Test monthly report string representation"""
        expected_str = f"Monthly Report - {self.year}/{self.month}"
        self.assertEqual(str(self.monthly_report), expected_str)

    def test_monthly_report_update(self):
        """Test monthly report update"""
        self.monthly_report.total_revenue = Decimal('35000.00')
        self.monthly_report.total_reservations = 1750
        self.monthly_report.save()
        
        updated_report = MonthlyReport.objects.get(id=self.monthly_report.id)
        self.assertEqual(updated_report.total_revenue, Decimal('35000.00'))
        self.assertEqual(updated_report.total_reservations, 1750)

    def test_monthly_report_validation(self):
        """Test monthly report validation"""
        # Test duplicate year/month
        with self.assertRaises(Exception):
            MonthlyReport.objects.create(
                year=self.year,
                month=self.month,
                total_revenue=Decimal('10000.00'),
                total_reservations=500
            )
        
        # Test invalid month
        with self.assertRaises(ValidationError):
            MonthlyReport.objects.create(
                year=2024,
                month=13,
                total_revenue=Decimal('10000.00'),
                total_reservations=500
            )
        
        # Test invalid year
        with self.assertRaises(ValidationError):
            MonthlyReport.objects.create(
                year=1899,  # Too old
                month=1,
                total_revenue=Decimal('10000.00'),
                total_reservations=500
            )

    def test_generate_report_empty_data(self):
        """Test generating report with no data"""
        report = MonthlyReport.generate_report(year=2025, month=1)  # Future date
        
        self.assertEqual(report.year, 2025)
        self.assertEqual(report.month, 1)
        self.assertEqual(report.total_revenue, Decimal('0.00'))
        self.assertEqual(report.total_reservations, 0)
        self.assertEqual(report.average_duration, 0)
        self.assertEqual(report.average_occupancy_rate, 0)
        self.assertIsNone(report.peak_day)

class ParkingLotReportModelTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username='owneruser',
            email='owner@example.com',
            password='ownerpass123',
            first_name='Owner',
            last_name='User',
            role='user'
        )
        self.parking_lot = ParkingLot.objects.create(
            name='Test Parking Lot',
            address='123 Test Street',
            total_spaces=50,
            hourly_rate=Decimal('10.00'),
            owner=self.owner
        )
        self.date = datetime.now().date()
        self.parking_lot_report = ParkingLotReport.objects.create(
            parking_lot=self.parking_lot,
            date=self.date,
            total_revenue=Decimal('5000.00'),
            total_reservations=250,
            occupancy_rate=85.0,
            average_duration=2.5,
            peak_hour=datetime.now().time()
        )

    def test_parking_lot_report_creation(self):
        """Test parking lot report creation"""
        self.assertEqual(self.parking_lot_report.parking_lot, self.parking_lot)
        self.assertEqual(self.parking_lot_report.date, self.date)
        self.assertEqual(self.parking_lot_report.total_revenue, Decimal('5000.00'))
        self.assertEqual(self.parking_lot_report.total_reservations, 250)
        self.assertEqual(self.parking_lot_report.occupancy_rate, 85.0)
        self.assertEqual(self.parking_lot_report.average_duration, 2.5)

    def test_parking_lot_report_str(self):
        """Test parking lot report string representation"""
        expected_str = f"{self.parking_lot.name} - {self.date}"
        self.assertEqual(str(self.parking_lot_report), expected_str)

    def test_parking_lot_report_update(self):
        """Test parking lot report update"""
        self.parking_lot_report.total_revenue = Decimal('6000.00')
        self.parking_lot_report.total_reservations = 300
        self.parking_lot_report.save()
        
        updated_report = ParkingLotReport.objects.get(id=self.parking_lot_report.id)
        self.assertEqual(updated_report.total_revenue, Decimal('6000.00'))
        self.assertEqual(updated_report.total_reservations, 300)

    def test_parking_lot_report_validation(self):
        """Test parking lot report validation"""
        # Test duplicate parking lot and date
        with self.assertRaises(Exception):
            ParkingLotReport.objects.create(
                parking_lot=self.parking_lot,
                date=self.date,
                total_revenue=Decimal('2000.00'),
                total_reservations=100
            )

    def test_parking_lot_relationship(self):
        """Test parking lot relationship"""
        # Test that report is deleted when parking lot is deleted
        parking_lot_id = self.parking_lot.id
        self.parking_lot.delete()
        
        with self.assertRaises(ParkingLotReport.DoesNotExist):
            ParkingLotReport.objects.get(id=self.parking_lot_report.id)

    def test_generate_report_empty_data(self):
        """Test generating report with no reservations"""
        test_date = datetime.now().date() + timedelta(days=1)  # Use future date
        report = ParkingLotReport.generate_report(
            parking_lot=self.parking_lot,
            date=test_date
        )
        
        self.assertEqual(report.parking_lot, self.parking_lot)
        self.assertEqual(report.date, test_date)
        self.assertEqual(report.total_revenue, Decimal('0.00'))
        self.assertEqual(report.total_reservations, 0)
        self.assertEqual(report.occupancy_rate, 0)
        self.assertEqual(report.average_duration, 0)
        self.assertIsNone(report.peak_hour) 