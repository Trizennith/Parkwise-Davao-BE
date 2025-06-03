from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.utils import timezone
from app.api.accounts.serializers import UserSerializer
from .models import Reservation
from .serializers import (
    ReservationSerializer,
    ReservationCreateSerializer,
    ReservationUpdateSerializer
)
from .services import ReservationService
from rest_framework.decorators import action
from django.db.models import Q
from datetime import datetime
from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    """Custom pagination class for consistent page sizes."""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

# Create your views here.

class ReservationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing reservations."""
    
    queryset = Reservation.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ReservationCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ReservationUpdateSerializer
        return ReservationSerializer
    
    def get_queryset(self):
        """Filter reservations based on user role and query parameters."""
        queryset = Reservation.objects.all()
        
        # Regular users can only see their own reservations
        if not self.request.user.is_admin:
            queryset = queryset.filter(user=self.request.user)
        
        # Filter by status if provided
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by parking lot if provided
        parking_lot = self.request.query_params.get('parking_lot')
        if parking_lot:
            queryset = queryset.filter(parking_lot=parking_lot)
            
        # Filter by parking space if provided
        parking_space = self.request.query_params.get('parking_space')
        if parking_space:
            queryset = queryset.filter(parking_space=parking_space)
            
        # Filter by vehicle plate if provided
        vehicle_plate = self.request.query_params.get('vehicle_plate')
        if vehicle_plate:
            queryset = queryset.filter(vehicle_plate__icontains=vehicle_plate)
            
        # Filter by date range if provided
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                queryset = queryset.filter(start_time__date__gte=start_date)
            except ValueError:
                pass
                
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
                queryset = queryset.filter(end_time__date__lte=end_date)
            except ValueError:
                pass
                
        # Filter by active/completed/cancelled
        status_filter = self.request.query_params.get('status_filter')
        if status_filter:
            if status_filter == 'active':
                queryset = queryset.filter(status='active')
            elif status_filter == 'completed':
                queryset = queryset.filter(status='completed')
            elif status_filter == 'cancelled':
                queryset = queryset.filter(status='cancelled')
                
        # Search functionality
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(vehicle_plate__icontains=search) |
                Q(notes__icontains=search) |
                Q(parking_lot__name__icontains=search) |
                Q(parking_space__space_number__icontains=search)
            )
            
        # Sorting
        sort_by = self.request.query_params.get('sort_by', '-created_at')
        if sort_by:
            # Validate sort fields to prevent SQL injection
            allowed_sort_fields = {
                'created_at', '-created_at',
                'start_time', '-start_time',
                'end_time', '-end_time',
                'status', '-status',
                'vehicle_plate', '-vehicle_plate'
            }
            if sort_by in allowed_sort_fields:
                queryset = queryset.order_by(sort_by)
        
        return queryset
    
    def perform_create(self, serializer):
        """Create a new reservation using the service."""
        validated_data = serializer.validated_data
        reservation = ReservationService.create_reservation(
            user=self.request.user,
            parking_lot=validated_data['parking_lot'],
            start_time=validated_data['start_time'],
            end_time=validated_data['end_time'],
            vehicle_plate=validated_data.get('vehicle_plate'),
            notes=validated_data.get('notes'),
            parking_space=validated_data.get('parking_space')
        )
        serializer.instance = reservation
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a reservation using the service."""
        try:
            reservation = ReservationService.cancel_reservation(pk, request.user)
            return Response(
                {'detail': 'Reservation cancelled successfully.'},
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark a reservation as completed using the service."""
        try:
            reservation = ReservationService.update_reservation_status(
                pk, 
                'completed',
                request.user
            )
            return Response(
                {'detail': 'Reservation marked as completed.'},
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def my_reservations(self, request):
        """Get current user's reservations."""
        reservations = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(reservations, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active reservations."""
        reservations = ReservationService.get_user_active_reservations(request.user)
        serializer = self.get_serializer(reservations, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending reservations."""
        reservations = ReservationService.get_user_pending_reservations(request.user)
        serializer = self.get_serializer(reservations, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def expired(self, request):
        """Get expired reservations."""
        reservations = ReservationService.get_user_expired_reservations(request.user)
        serializer = self.get_serializer(reservations, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def cancelled(self, request):
        """Get cancelled reservations."""
        reservations = ReservationService.get_user_cancelled_reservations(request.user)
        serializer = self.get_serializer(reservations, many=True)
        return Response(serializer.data)
