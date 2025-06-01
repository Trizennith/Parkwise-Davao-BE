from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import ParkingLot, ParkingSpace
from .serializers import ParkingLotSerializer, ParkingLotCreateSerializer, ParkingLotUpdateSerializer, ParkingSpaceSerializer

# Create your views here.

class ParkingLotViewSet(viewsets.ModelViewSet):
    """ViewSet for managing parking lots."""
    
    queryset = ParkingLot.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ParkingLotCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ParkingLotUpdateSerializer
        return ParkingLotSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]
    
    @action(detail=True, methods=['get'])
    def available_spaces(self, request, pk=None):
        """Get available spaces in a parking lot."""
        parking_lot = self.get_object()
        available_spaces = parking_lot.spaces.filter(
            status=ParkingSpace.Status.AVAILABLE
        )
        serializer = ParkingSpaceSerializer(available_spaces, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def occupancy_rate(self, request, pk=None):
        """Get the occupancy rate of a parking lot."""
        parking_lot = self.get_object()
        return Response({
            'occupancy_rate': parking_lot.occupancy_rate
        })

class ParkingSpaceViewSet(viewsets.ModelViewSet):
    """ViewSet for managing parking spaces."""
    
    queryset = ParkingSpace.objects.all()
    serializer_class = ParkingSpaceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]
    
    def get_queryset(self):
        """Filter spaces by parking lot if lot_id is provided."""
        queryset = ParkingSpace.objects.all()
        lot_id = self.request.query_params.get('lot_id')
        if lot_id:
            queryset = queryset.filter(parking_lot_id=lot_id)
        return queryset
    
    @action(detail=True, methods=['post'])
    def reserve(self, request, pk=None):
        """Reserve a parking space."""
        space = self.get_object()
        
        if space.status != ParkingSpace.Status.AVAILABLE:
            return Response(
                {'detail': 'This space is not available for reservation.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        space.status = ParkingSpace.Status.RESERVED
        space.current_user = request.user
        space.save()
        
        return Response(
            {'detail': 'Space reserved successfully.'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def occupy(self, request, pk=None):
        """Mark a space as occupied."""
        space = self.get_object()
        
        if space.status not in [ParkingSpace.Status.AVAILABLE, ParkingSpace.Status.RESERVED]:
            return Response(
                {'detail': 'This space cannot be occupied.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        space.status = ParkingSpace.Status.OCCUPIED
        space.current_user = request.user
        space.save()
        
        # Update parking lot available spaces
        parking_lot = space.parking_lot
        parking_lot.available_spaces = max(0, parking_lot.available_spaces - 1)
        parking_lot.save()
        
        return Response(
            {'detail': 'Space marked as occupied.'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def vacate(self, request, pk=None):
        """Mark a space as available."""
        space = self.get_object()
        
        if space.status != ParkingSpace.Status.OCCUPIED:
            return Response(
                {'detail': 'This space is not occupied.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        space.status = ParkingSpace.Status.AVAILABLE
        space.current_user = None
        space.save()
        
        # Update parking lot available spaces
        parking_lot = space.parking_lot
        parking_lot.available_spaces = min(
            parking_lot.total_spaces,
            parking_lot.available_spaces + 1
        )
        parking_lot.save()
        
        return Response(
            {'detail': 'Space marked as available.'},
            status=status.HTTP_200_OK
        )
