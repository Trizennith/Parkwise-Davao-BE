from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .middleware import WebSocketTokenManager

class WebSocketTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Generate a WebSocket token for the authenticated user."""
        token = WebSocketTokenManager.generate_ws_token(request.user.id)
        return Response({'ws_token': token}) 