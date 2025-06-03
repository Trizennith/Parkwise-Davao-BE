from django.utils import timezone
from django.db import transaction
from app.api.reservations.models import Reservation
from app.websocket.notification_service import NotificationService
from datetime import timedelta

class ReservationService:
    @staticmethod
    def create_reservation(user, parking_lot, start_time, end_time, **kwargs):
        """
        Create a new reservation and send notification
        """
        with transaction.atomic():
            # Create the reservation
            reservation = Reservation.objects.create(
                user=user,
                parking_lot=parking_lot,
                start_time=start_time,
                end_time=end_time,
                **kwargs
            )
            
            # Send notification
            NotificationService.notify_new_reservation(reservation)
            
            return reservation

    @staticmethod
    def cancel_reservation(reservation_id, user):
        """
        Cancel a reservation and send notification
        """
        with transaction.atomic():
            try:
                reservation = Reservation.objects.get(id=reservation_id, user=user)
                
                if reservation.status == 'cancelled':
                    raise ValueError("Reservation is already cancelled")
                
                if reservation.status == 'expired':
                    raise ValueError("Cannot cancel an expired reservation")
                
                reservation.status = 'cancelled'
                reservation.save()
                
                # Send notification
                NotificationService.notify_reservation_cancelled(reservation)
                
                return reservation
            except Reservation.DoesNotExist:
                raise ValueError("Reservation not found")

    @staticmethod
    def check_expired_reservations():
        """
        Check and update expired reservations
        """
        NotificationService.check_expired_reservations()

    @staticmethod
    def check_upcoming_reservations():
        """
        Check and notify about upcoming reservations
        """
        NotificationService.check_upcoming_reservations()

    @staticmethod
    def get_user_active_reservations(user):
        """
        Get user's active reservations
        """
        return Reservation.objects.filter(
            user=user,
            status='active',
            end_time__gt=timezone.now()
        )

    @staticmethod
    def get_user_pending_reservations(user):
        """
        Get user's pending reservations
        """
        return Reservation.objects.filter(
            user=user,
            status='pending',
            start_time__gt=timezone.now()
        )

    @staticmethod
    def get_user_expired_reservations(user):
        """
        Get user's expired reservations
        """
        return Reservation.objects.filter(
            user=user,
            status='expired'
        )

    @staticmethod
    def get_user_cancelled_reservations(user):
        """
        Get user's cancelled reservations
        """
        return Reservation.objects.filter(
            user=user,
            status='cancelled'
        )

    @staticmethod
    def update_reservation_status(reservation_id, new_status, user):
        """
        Update reservation status and send appropriate notification
        """
        with transaction.atomic():
            try:
                reservation = Reservation.objects.get(id=reservation_id, user=user)
                
                if reservation.status == new_status:
                    return reservation
                
                reservation.status = new_status
                reservation.save()
                
                # Send appropriate notification based on status
                if new_status == 'cancelled':
                    NotificationService.notify_reservation_cancelled(reservation)
                elif new_status == 'expired':
                    NotificationService.notify_reservation_expired(reservation)
                
                return reservation
            except Reservation.DoesNotExist:
                raise ValueError("Reservation not found")

    @staticmethod
    def get_reservation_details(reservation_id, user):
        """
        Get detailed information about a reservation
        """
        try:
            return Reservation.objects.get(id=reservation_id, user=user)
        except Reservation.DoesNotExist:
            raise ValueError("Reservation not found") 