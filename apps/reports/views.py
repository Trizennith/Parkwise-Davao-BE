from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Count, Sum, Avg
from django.db.models.functions import TruncDate, TruncHour
from datetime import timedelta
from .models import DailyReport, ParkingLotReport
from .serializers import (
    DailyReportSerializer, ParkingLotReportSerializer,
    ReportSummarySerializer, DailyReservationsSerializer,
    RevenueSerializer, PeakHoursSerializer,
    UserDemographicsSerializer
)
from apps.reservations.models import Reservation
from apps.parking_lots.models import ParkingLot

class ReportViewSet(viewsets.ViewSet):
    """ViewSet for generating and retrieving reports."""
    
    permission_classes = [permissions.IsAdminUser]
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get summary of current day's statistics."""
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        # Get today's data
        today_reservations = Reservation.objects.filter(
            start_time__date=today,
            status__in=['active', 'completed']
        )
        today_revenue = sum(r.total_cost for r in today_reservations)
        today_count = today_reservations.count()
        today_duration = sum(r.duration for r in today_reservations) / today_count if today_count > 0 else 0
        
        # Get yesterday's data for comparison
        yesterday_reservations = Reservation.objects.filter(
            start_time__date=yesterday,
            status__in=['active', 'completed']
        )
        yesterday_revenue = sum(r.total_cost for r in yesterday_reservations)
        yesterday_count = yesterday_reservations.count()
        yesterday_duration = sum(r.duration for r in yesterday_reservations) / yesterday_count if yesterday_count > 0 else 0
        
        # Calculate overall parking utilization
        total_spaces = sum(lot.total_spaces for lot in ParkingLot.objects.all())
        occupied_spaces = sum(lot.total_spaces - lot.available_spaces for lot in ParkingLot.objects.all())
        utilization = (occupied_spaces / total_spaces * 100) if total_spaces > 0 else 0
        
        # Calculate yesterday's utilization
        yesterday_utilization = DailyReport.objects.filter(date=yesterday).first()
        yesterday_utilization = yesterday_utilization.occupancy_rate if yesterday_utilization else 0
        
        data = {
            'total_revenue': today_revenue,
            'daily_reservations': today_count,
            'parking_utilization': utilization,
            'average_duration': today_duration,
            'revenue_change': today_revenue - yesterday_revenue,
            'reservation_change': today_count - yesterday_count,
            'utilization_change': utilization - yesterday_utilization,
            'duration_change': today_duration - yesterday_duration
        }
        
        serializer = ReportSummarySerializer(data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def daily_reservations(self, request):
        """Get daily reservations data for the last 7 days."""
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=6)
        
        reservations = Reservation.objects.filter(
            start_time__date__range=[start_date, end_date],
            status__in=['active', 'completed']
        ).annotate(
            date=TruncDate('start_time')
        ).values('date').annotate(
            reservations=Count('id')
        ).order_by('date')
        
        serializer = DailyReservationsSerializer(reservations, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def revenue(self, request):
        """Get revenue data for the last 7 days."""
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=6)
        
        reservations = Reservation.objects.filter(
            start_time__date__range=[start_date, end_date],
            status__in=['active', 'completed']
        ).annotate(
            date=TruncDate('start_time')
        ).values('date').annotate(
            revenue=Sum('total_cost')
        ).order_by('date')
        
        serializer = RevenueSerializer(reservations, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def peak_hours(self, request):
        """Get peak hours data for today."""
        today = timezone.now().date()
        
        reservations = Reservation.objects.filter(
            start_time__date=today,
            status__in=['active', 'completed']
        ).annotate(
            hour=TruncHour('start_time')
        ).values('hour').annotate(
            usage=Count('id')
        ).order_by('hour')
        
        serializer = PeakHoursSerializer(reservations, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def user_demographics(self, request):
        """Get user demographics data."""
        # Get user counts by role
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        user_counts = User.objects.values('role').annotate(
            value=Count('id')
        ).values('role', 'value')
        
        # Format data for the serializer
        data = [
            {'name': role, 'value': count}
            for role, count in user_counts
        ]
        
        serializer = UserDemographicsSerializer(data, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def parking_lot(self, request, pk=None):
        """Get detailed report for a specific parking lot."""
        try:
            parking_lot = ParkingLot.objects.get(pk=pk)
        except ParkingLot.DoesNotExist:
            return Response(
                {'detail': 'Parking lot not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Generate report for today
        report = ParkingLotReport.generate_report(
            parking_lot=parking_lot,
            date=timezone.now().date()
        )
        
        serializer = ParkingLotReportSerializer(report)
        return Response(serializer.data) 