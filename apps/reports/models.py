from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from apps.parking_lots.models import ParkingLot
from apps.reservations.models import Reservation

User = get_user_model()

class DailyReport(models.Model):
    """Model for daily parking reports."""
    
    date = models.DateField(_('date'), unique=True)
    total_revenue = models.DecimalField(
        _('total revenue'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    total_reservations = models.PositiveIntegerField(
        _('total reservations'),
        default=0
    )
    average_duration = models.FloatField(
        _('average duration'),
        default=0
    )
    peak_hour = models.TimeField(_('peak hour'), null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('daily report')
        verbose_name_plural = _('daily reports')
        ordering = ['-date']
    
    def __str__(self):
        return f"Daily Report - {self.date}"
    
    @classmethod
    def generate_report(cls, date):
        """Generate a daily report for the specified date."""
        # Get all reservations for the date
        reservations = Reservation.objects.filter(
            start_time__date=date,
            status__in=['active', 'completed']
        )
        
        # Calculate total revenue
        total_revenue = sum(reservation.total_cost for reservation in reservations)
        
        # Calculate total reservations
        total_reservations = reservations.count()
        
        # Calculate average duration
        durations = [reservation.duration for reservation in reservations]
        average_duration = sum(durations) / len(durations) if durations else 0
        
        # Find peak hour
        hourly_counts = {}
        for reservation in reservations:
            hour = reservation.start_time.hour
            hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
        
        peak_hour = max(hourly_counts.items(), key=lambda x: x[1])[0] if hourly_counts else None
        
        # Create or update report
        report, created = cls.objects.update_or_create(
            date=date,
            defaults={
                'total_revenue': total_revenue,
                'total_reservations': total_reservations,
                'average_duration': average_duration,
                'peak_hour': peak_hour
            }
        )
        
        return report

class ParkingLotReport(models.Model):
    """Model for parking lot specific reports."""
    
    parking_lot = models.ForeignKey(
        ParkingLot,
        on_delete=models.CASCADE,
        related_name='reports'
    )
    date = models.DateField(_('date'))
    total_revenue = models.DecimalField(
        _('total revenue'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    total_reservations = models.PositiveIntegerField(
        _('total reservations'),
        default=0
    )
    occupancy_rate = models.FloatField(
        _('occupancy rate'),
        default=0
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('parking lot report')
        verbose_name_plural = _('parking lot reports')
        ordering = ['-date', 'parking_lot']
        unique_together = ['parking_lot', 'date']
    
    def __str__(self):
        return f"{self.parking_lot.name} - {self.date}"
    
    @classmethod
    def generate_report(cls, parking_lot, date):
        """Generate a report for a specific parking lot and date."""
        # Get all reservations for the parking lot and date
        reservations = Reservation.objects.filter(
            parking_lot=parking_lot,
            start_time__date=date,
            status__in=['active', 'completed']
        )
        
        # Calculate total revenue
        total_revenue = sum(reservation.total_cost for reservation in reservations)
        
        # Calculate total reservations
        total_reservations = reservations.count()
        
        # Calculate occupancy rate
        occupancy_rate = parking_lot.occupancy_rate
        
        # Create or update report
        report, created = cls.objects.update_or_create(
            parking_lot=parking_lot,
            date=date,
            defaults={
                'total_revenue': total_revenue,
                'total_reservations': total_reservations,
                'occupancy_rate': occupancy_rate
            }
        )
        
        return report 