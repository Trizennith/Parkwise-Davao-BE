# WebSocket Implementation Guide

## Overview
This guide explains how to implement real-time notifications using WebSockets in the Smart Parking Davao application. The system uses a secure token-based authentication system specifically for WebSocket connections.

## Security Features
- Short-lived WebSocket tokens (30 minutes)
- Token-based authentication
- Cache-based token verification
- Separate from main JWT authentication
- Automatic token expiration

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
ws://localhost:8011/ws/notifications/?token=your_websocket_token
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
Create a custom hook for WebSocket management:

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

      const ws = new WebSocket(`ws://localhost:8011/ws/notifications/?token=${wsToken}`);
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
Create a component to display notifications:

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

### 3. Usage in App
```typescript
// App.tsx
import { NotificationCenter } from './components/NotificationCenter';

function App() {
  return (
    <div className="app">
      <header>
        <h1>Smart Parking Davao</h1>
        <NotificationCenter />
      </header>
      {/* Rest of your app */}
    </div>
  );
}
```

### 4. Styling Example
```css
/* styles/NotificationCenter.css */
.notification-center {
  position: fixed;
  top: 20px;
  right: 20px;
  width: 300px;
  max-height: 400px;
  overflow-y: auto;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  z-index: 1000;
}

.connection-status {
  padding: 10px;
  background: #f5f5f5;
  border-bottom: 1px solid #eee;
  font-size: 12px;
}

.notifications {
  padding: 10px;
}

.notification {
  padding: 10px;
  margin-bottom: 10px;
  border-radius: 4px;
  background: #f8f9fa;
  border-left: 4px solid #007bff;
}

.notification h4 {
  margin: 0 0 5px 0;
  font-size: 14px;
}

.notification pre {
  margin: 0;
  font-size: 12px;
  white-space: pre-wrap;
}
```

## Error Handling

### 1. Token Expiration
When the WebSocket token expires (after 30 minutes), the connection will close. The hook will automatically attempt to:
1. Get a new WebSocket token
2. Reconnect to the WebSocket
3. Resubscribe to notifications

### 2. Connection Issues
The hook includes automatic reconnection logic:
- Attempts to reconnect every 5 seconds after disconnection
- Handles network errors gracefully
- Provides connection status to the UI

## Best Practices

1. **Token Management**
   - Always use the WebSocket token endpoint to get tokens
   - Don't store WebSocket tokens in localStorage
   - Handle token expiration gracefully

2. **Connection Management**
   - Implement reconnection logic
   - Show connection status to users
   - Handle disconnections gracefully

3. **Message Handling**
   - Validate message structure
   - Handle different message types appropriately
   - Implement error boundaries for message processing

4. **Performance**
   - Limit the number of stored messages
   - Implement message cleanup
   - Use appropriate message queuing

## Testing

### 1. Connection Test
```typescript
// Test connection
const { isConnected } = useWebSocket();
console.log('WebSocket connected:', isConnected);
```

### 2. Message Test
```typescript
// Test message handling
const { messages } = useWebSocket();
useEffect(() => {
  console.log('New message:', messages[messages.length - 1]);
}, [messages]);
```

## Troubleshooting

1. **Connection Issues**
   - Check if the WebSocket server is running
   - Verify the WebSocket URL is correct
   - Ensure the token is valid and not expired

2. **Authentication Issues**
   - Verify JWT token is valid
   - Check WebSocket token generation
   - Ensure proper headers are set

3. **Message Issues**
   - Verify message format
   - Check subscription types
   - Monitor WebSocket console for errors 