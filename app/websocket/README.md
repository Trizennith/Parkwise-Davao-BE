# WebSocket Implementation Guide

## Overview
This guide explains how to implement real-time notifications using WebSockets in the Smart Parking Davao application. The system uses a secure token-based authentication system specifically for WebSocket connections.

## Security Features
- Short-lived WebSocket tokens (30 minutes)
- Token-based authentication
- Cache-based token verification
- Separate from main JWT authentication
- Automatic token expiration

## Setup

### 1. Dependencies
Make sure you have the required packages:
```bash
pip install channels channels-redis daphne
```

### 2. Redis Configuration
The WebSocket system requires Redis for the channel layer. In development, you can use Docker:
```bash
docker run -d -p 6379:6379 redis:8.0.1-alpine
```

### 3. Environment Variables
```env
REDIS_HOST=localhost  # or 'redis' if using Docker
REDIS_PORT=6379
```

## Backend Implementation

### 1. WebSocket Token Generation
To get a WebSocket token, make a GET request to:
```
GET /api/user/ws-token/
Headers: {
    'Authorization': 'Bearer your_jwt_token'
}
```

Response:
```json
{
    "ws_token": "your_websocket_token"
}
```

### 2. WebSocket Connection
Connect to the WebSocket endpoint:
```
ws://localhost:8000/ws/notifications/?token=your_websocket_token
```

### 3. Message Types

#### Client to Server
```json
{
    "type": "subscribe",
    "notification_types": ["reservation", "parking_lot"]
}
```

#### Server to Client
```json
{
    "type": "notification",
    "message": "New reservation created",
    "data": {
        "reservation_id": 123,
        "status": "active"
    }
}
```

## Frontend Implementation (React)

### 1. WebSocket Hook
```typescript
// hooks/useWebSocket.ts
import { useEffect, useRef, useCallback, useState } from 'react';
import { useAuth } from './useAuth'; // Your auth context/hook

interface WebSocketMessage {
  type: string;
  message: string;
  data?: any;
}

export const useWebSocket = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState<WebSocketMessage[]>([]);
  const wsRef = useRef<WebSocket | null>(null);
  const { token } = useAuth(); // Your JWT token

  const getWebSocketToken = async () => {
    try {
      const response = await fetch('/api/user/ws-token/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const { ws_token } = await response.json();
      return ws_token;
    } catch (error) {
      console.error('Failed to get WebSocket token:', error);
      return null;
    }
  };

  const connect = useCallback(async () => {
    try {
      const wsToken = await getWebSocketToken();
      if (!wsToken) return;

      const ws = new WebSocket(`ws://localhost:8000/ws/notifications/?token=${wsToken}`);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        // Subscribe to notification types
        ws.send(JSON.stringify({
          type: 'subscribe',
          notification_types: ['reservation', 'parking_lot']
        }));
      };

      ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        setMessages(prev => [...prev, message]);
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setIsConnected(false);
      };

      ws.onclose = () => {
        setIsConnected(false);
        // Attempt to reconnect after 5 seconds
        setTimeout(connect, 5000);
      };
    } catch (error) {
      console.error('WebSocket connection error:', error);
    }
  }, [token]);

  useEffect(() => {
    connect();
    return () => {
      wsRef.current?.close();
    };
  }, [connect]);

  return { isConnected, messages };
};
```

### 2. Notification Component
```typescript
// components/NotificationCenter.tsx
import React from 'react';
import { useWebSocket } from '../hooks/useWebSocket';

export const NotificationCenter: React.FC = () => {
  const { isConnected, messages } = useWebSocket();

  return (
    <div className="notification-center">
      <div className="connection-status">
        Status: {isConnected ? 'Connected' : 'Disconnected'}
      </div>
      
      <div className="notifications">
        {messages.map((msg, index) => (
          <div key={index} className={`notification ${msg.type}`}>
            <h4>{msg.message}</h4>
            {msg.data && (
              <pre>{JSON.stringify(msg.data, null, 2)}</pre>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
```

## Troubleshooting

### Common Issues

1. **Connection Refused (403)**
   - Make sure you're using a WebSocket token, not a JWT token
   - Verify the token hasn't expired
   - Check if Redis is running and accessible

2. **Connection Timeout**
   - Verify the WebSocket server is running
   - Check if the port is correct (8000)
   - Ensure no firewall is blocking the connection

3. **Token Verification Failed**
   - Make sure you're getting a fresh WebSocket token
   - Check if Redis is properly configured
   - Verify the token format is correct

### Debugging

1. **Enable Debug Logging**
   The system includes detailed logging. Check your console for:
   - Token verification steps
   - Connection attempts
   - Message handling

2. **Check Redis**
   ```bash
   # Connect to Redis CLI
   redis-cli
   
   # Check if tokens are stored
   KEYS ws_token_*
   ```

3. **Verify Token**
   ```python
   # In Django shell
   from app.websocket.middleware import WebSocketTokenManager
   WebSocketTokenManager.verify_ws_token('your_token')
   ```

## Best Practices

1. **Token Management**
   - Always use the WebSocket token endpoint
   - Don't store WebSocket tokens in localStorage
   - Handle token expiration gracefully

2. **Connection Management**
   - Implement reconnection logic
   - Show connection status to users
   - Handle disconnections gracefully

3. **Message Handling**
   - Validate message structure
   - Handle different message types appropriately
   - Implement error boundaries

4. **Performance**
   - Limit stored messages
   - Implement message cleanup
   - Use appropriate message queuing

## Production Deployment

1. **Docker Setup**
   ```yaml
   # docker-compose.yml
   services:
     redis:
       image: redis:8.0.1-alpine
       ports:
         - "6379:6379"
   
     backend:
       build: .
       environment:
         - REDIS_HOST=redis
         - REDIS_PORT=6379
   ```

2. **Nginx Configuration**
   ```nginx
   location /ws/ {
       proxy_pass http://backend:8000;
       proxy_http_version 1.1;
       proxy_set_header Upgrade $http_upgrade;
       proxy_set_header Connection "upgrade";
       proxy_set_header Host $host;
   }
   ```

## Testing

1. **Connection Test**
   ```typescript
   const { isConnected } = useWebSocket();
   console.log('WebSocket connected:', isConnected);
   ```

2. **Message Test**
   ```typescript
   const { messages } = useWebSocket();
   useEffect(() => {
     console.log('New message:', messages[messages.length - 1]);
   }, [messages]);
   ```

## Support

If you encounter any issues:
1. Check the debug logs
2. Verify Redis connection
3. Ensure proper token generation
4. Check network connectivity

For more help, contact the development team or create an issue in the repository. 