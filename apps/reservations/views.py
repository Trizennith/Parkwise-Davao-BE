from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.utils import timezone
from apps.accounts.serializers import UserSerializer
from .models import Reservation
from .serializers import (
    ReservationSerializer,
    ReservationCreateSerializer,
    ReservationUpdateSerializer
)
from rest_framework.decorators import action

# Create your views here.

class ReservationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing reservations."""
    
    queryset = Reservation.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
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
        
        return queryset
    
    def perform_create(self, serializer):
        """Create a new reservation."""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a reservation."""
        reservation = self.get_object()
        
        if reservation.status != Reservation.Status.ACTIVE:
            return Response(
                {'detail': 'Only active reservations can be cancelled.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reservation.status = Reservation.Status.CANCELLED
        reservation.save()
        
        return Response(
            {'detail': 'Reservation cancelled successfully.'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark a reservation as completed."""
        reservation = self.get_object()
        
        if reservation.status != Reservation.Status.ACTIVE:
            return Response(
                {'detail': 'Only active reservations can be completed.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reservation.status = Reservation.Status.COMPLETED
        reservation.save()
        
        return Response(
            {'detail': 'Reservation marked as completed.'},
            status=status.HTTP_200_OK
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
        reservations = self.get_queryset().filter(
            status=Reservation.Status.ACTIVE,
            end_time__gt=timezone.now()
        )
        serializer = self.get_serializer(reservations, many=True)
        return Response(serializer.data)
