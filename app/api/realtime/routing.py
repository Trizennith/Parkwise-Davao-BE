from django.urls import re_path
from . import consumers
import logging

logger = logging.getLogger(__name__)

# Define WebSocket URL patterns
websocket_urlpatterns = [
    re_path(r'^ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
]

logger.debug(f"Registered WebSocket patterns: {websocket_urlpatterns}") 