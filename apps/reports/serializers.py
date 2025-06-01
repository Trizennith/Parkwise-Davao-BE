from rest_framework import serializers
from .models import DailyReport, ParkingLotReport

class DailyReportSerializer(serializers.ModelSerializer):
    """Serializer for daily reports."""
    
    class Meta:
        model = DailyReport
        fields = (
            'date', 'total_revenue', 'total_reservations',
            'average_duration', 'peak_hour', 'created_at',
            'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at')

class ParkingLotReportSerializer(serializers.ModelSerializer):
    """Serializer for parking lot reports."""
    
    parking_lot_name = serializers.CharField(
        source='parking_lot.name',
        read_only=True
    )
    
    class Meta:
        model = ParkingLotReport
        fields = (
            'parking_lot', 'parking_lot_name', 'date',
            'total_revenue', 'total_reservations',
            'occupancy_rate', 'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at')

class ReportSummarySerializer(serializers.Serializer):
    """Serializer for report summary."""
    
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    daily_reservations = serializers.IntegerField()
    parking_utilization = serializers.FloatField()
    average_duration = serializers.FloatField()
    revenue_change = serializers.DecimalField(max_digits=10, decimal_places=2)
    reservation_change = serializers.IntegerField()
    utilization_change = serializers.FloatField()
    duration_change = serializers.FloatField()

class DailyReservationsSerializer(serializers.Serializer):
    """Serializer for daily reservations data."""
    
    date = serializers.DateField()
    reservations = serializers.IntegerField()

class RevenueSerializer(serializers.Serializer):
    """Serializer for revenue data."""
    
    date = serializers.DateField()
    revenue = serializers.DecimalField(max_digits=10, decimal_places=2)

class PeakHoursSerializer(serializers.Serializer):
    """Serializer for peak hours data."""
    
    hour = serializers.TimeField()
    usage = serializers.IntegerField()

class UserDemographicsSerializer(serializers.Serializer):
    """Serializer for user demographics data."""
    
    name = serializers.CharField()
    value = serializers.IntegerField() 