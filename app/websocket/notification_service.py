from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from app.api.reservations.models import Reservation
from app.api.notification.models import Notification
from datetime import datetime, timedelta
from django.utils import timezone

class NotificationService:
    @staticmethod
    def send_reservation_notification(user_id, notification_type, message, data=None):
        """
        Send a notification to a specific user about their reservation
        """
        # Save notification to database
        notification = Notification.objects.create(
            user_id=user_id,
            type=notification_type,
            message=message,
            data=data or {}
        )

        # Send WebSocket notification
        channel_layer = get_channel_layer()
        group_name = f"user_{user_id}_notifications"
        
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'send_notification',
                'type': notification_type,
                'message': message,
                'data': {
                    **(data or {}),
                    'notification_id': notification.id,
                    'created_at': notification.created_at.isoformat()
                }
            }
        )

    @staticmethod
    def notify_new_reservation(reservation):
        """
        Notify user about a new reservation
        """
        NotificationService.send_reservation_notification(
            reservation.user.id,
            Notification.NotificationType.NEW_RESERVATION,
            'New reservation created',
            {
                'reservation_id': reservation.id,
                'parking_lot': reservation.parking_lot.name,
                'start_time': reservation.start_time.isoformat(),
                'end_time': reservation.end_time.isoformat()
            }
        )

    @staticmethod
    def notify_reservation_expired(reservation):
        """
        Notify user about an expired reservation
        """
        NotificationService.send_reservation_notification(
            reservation.user.id,
            Notification.NotificationType.RESERVATION_EXPIRED,
            'Your reservation has expired',
            {
                'reservation_id': reservation.id,
                'parking_lot': reservation.parking_lot.name
            }
        )

    @staticmethod
    def notify_reservation_cancelled(reservation):
        """
        Notify user about a cancelled reservation
        """
        NotificationService.send_reservation_notification(
            reservation.user.id,
            Notification.NotificationType.RESERVATION_CANCELLED,
            'Your reservation has been cancelled',
            {
                'reservation_id': reservation.id,
                'parking_lot': reservation.parking_lot.name
            }
        )

    @staticmethod
    def check_expired_reservations():
        """
        Check for expired reservations and send notifications
        """
        now = timezone.now()
        expired_reservations = Reservation.objects.filter(
            end_time__lt=now,
            status='active'
        )
        
        for reservation in expired_reservations:
            reservation.status = 'expired'
            reservation.save()
            NotificationService.notify_reservation_expired(reservation)

    @staticmethod
    def check_upcoming_reservations():
        """
        Check for upcoming reservations and send notifications
        """
        now = timezone.now()
        upcoming_time = now + timedelta(minutes=30)  # Notify 30 minutes before
        
        upcoming_reservations = Reservation.objects.filter(
            start_time__lte=upcoming_time,
            start_time__gt=now,
            status='pending'
        )
        
        for reservation in upcoming_reservations:
            NotificationService.send_reservation_notification(
                reservation.user.id,
                Notification.NotificationType.UPCOMING_RESERVATION,
                'You have an upcoming reservation',
                {
                    'reservation_id': reservation.id,
                    'parking_lot': reservation.parking_lot.name,
                    'start_time': reservation.start_time.isoformat()
                }
            ) 