import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from app.api.reservations.models import Reservation

logger = logging.getLogger(__name__)
User = get_user_model()

class ReservationConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_group_name = None
        self.user = None

    async def connect(self):
        logger.debug("Attempting WebSocket connection...")
        # Get the user from the scope
        self.user = self.scope["user"]
        logger.debug(f"User from scope: {self.user}")
        
        if not self.user.is_authenticated:
            logger.debug("User is not authenticated, closing connection")
            await self.close()
            return

        # Create a unique group name for the user
        self.room_group_name = f"user_{self.user.id}_notifications"
        logger.debug(f"Created room group name: {self.room_group_name}")

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        logger.debug("Successfully joined room group")

        await self.accept()
        logger.debug("WebSocket connection accepted")

    async def disconnect(self, close_code):
        logger.debug(f"Disconnecting with code: {close_code}")
        # Only try to leave the room group if we successfully joined it
        if self.room_group_name:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            logger.debug("Left room group")

    async def receive(self, text_data):
        logger.debug(f"Received message: {text_data}")
        # Handle any incoming messages from the client
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')

        if message_type == 'subscribe':
            # Handle subscription to specific notification types
            notification_types = text_data_json.get('notification_types', [])
            logger.debug(f"Subscribing to notification types: {notification_types}")
            # You can implement specific subscription logic here
            pass

    async def send_notification(self, event):
        logger.debug(f"Sending notification: {event}")
        # Send notification to WebSocket
        await self.send(text_data=json.dumps({
            'type': event['type'],
            'message': event['message'],
            'data': event.get('data', {})
        }))

    @database_sync_to_async
    def get_user_reservations(self):
        # Get user's active reservations
        return list(Reservation.objects.filter(user=self.user).values()) 