from channels.middleware import BaseMiddleware
from channels.auth import AuthMiddlewareStack
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from urllib.parse import parse_qs
from django.db import close_old_connections
from django.core.cache import cache
from datetime import timedelta
import jwt
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

User = get_user_model()

class WebSocketTokenManager:
    @staticmethod
    def generate_ws_token(user_id):
        """Generate a short-lived WebSocket token."""
        token = jwt.encode(
            {
                'user_id': user_id,
                'type': 'ws_token',
                'exp': int((settings.WS_TOKEN_LIFETIME).total_seconds())
            },
            settings.SECRET_KEY,
            algorithm='HS256'
        )
        # Store token in cache with expiration
        cache.set(f'ws_token_{user_id}', token, timeout=settings.WS_TOKEN_LIFETIME.total_seconds())
        logger.debug(f"Generated and cached WebSocket token for user {user_id}")
        return token

    @staticmethod
    def verify_ws_token(token):
        """Verify the WebSocket token."""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            logger.debug(f"Decoded token payload: {payload}")
            
            if payload.get('type') != 'ws_token':
                logger.debug("Token type mismatch")
                return None
                
            # Verify token is in cache
            cached_token = cache.get(f'ws_token_{payload["user_id"]}')
            logger.debug(f"Cached token exists: {cached_token is not None}")
            
            if cached_token != token:
                logger.debug("Token mismatch with cached token")
                return None
                
            return payload
        except jwt.InvalidTokenError as e:
            logger.debug(f"Invalid token error: {str(e)}")
            return None

class JWTAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        close_old_connections()

        # Get the token from the query string
        query_string = scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]
        
        logger.debug(f"Received WebSocket connection with token: {token}")

        if token:
            try:
                # First try to verify as WebSocket token
                payload = WebSocketTokenManager.verify_ws_token(token)
                if payload:
                    logger.debug(f"WebSocket token verified for user {payload['user_id']}")
                    user = await self.get_user(payload['user_id'])
                    scope['user'] = user
                else:
                    # If not a WebSocket token, try as JWT token
                    logger.debug("Attempting to verify as JWT token")
                    access_token = AccessToken(token)
                    user_id = access_token['user_id']
                    user = await self.get_user(user_id)
                    scope['user'] = user
            except Exception as e:
                logger.error(f"Error during token verification: {str(e)}")
                scope['user'] = AnonymousUser()
        else:
            logger.debug("No token provided")
            scope['user'] = AnonymousUser()

        return await self.inner(scope, receive, send)

    @staticmethod
    async def get_user(user_id):
        try:
            return await User.objects.aget(id=user_id)
        except User.DoesNotExist:
            logger.debug(f"User {user_id} not found")
            return AnonymousUser()

def JWTAuthMiddlewareStack(inner):
    return JWTAuthMiddleware(AuthMiddlewareStack(inner)) 