# Smart Parking Notification System Guide

This guide explains how to use the notification system for the Smart Parking application, which provides real-time notifications for reservation events and other important updates.

## Table of Contents
- [Overview](#overview)
- [Notification Types](#notification-types)
- [Backend Usage](#backend-usage)
- [Frontend Integration](#frontend-integration)
- [Database Structure](#database-structure)
- [WebSocket Events](#websocket-events)

## Overview

The notification system provides:
- Real-time notifications via WebSocket
- Persistent storage of notifications in the database
- Support for different notification types
- Read/unread status tracking
- Automatic notifications for reservation events

## Notification Types

The system supports the following notification types:
- `new_reservation`: When a new reservation is created
- `reservation_expired`: When a reservation expires
- `reservation_cancelled`: When a reservation is cancelled
- `upcoming_reservation`: 30 minutes before a reservation starts
- `custom`: For custom notifications

## Backend Usage

### 1. Sending Notifications

```python
from app.websocket.notification_service import NotificationService

# Send a custom notification
NotificationService.send_reservation_notification(
    user_id=user.id,
    notification_type='custom',
    message='Your custom message',
    data={'custom': 'data'}
)

# Send a reservation notification
NotificationService.notify_new_reservation(reservation)
NotificationService.notify_reservation_expired(reservation)
NotificationService.notify_reservation_cancelled(reservation)
```

### 2. Querying Notifications

```python
from app.notification.models import Notification

# Get all notifications for a user
notifications = Notification.objects.filter(user=user)

# Get unread notifications
unread_notifications = Notification.objects.filter(
    user=user, 
    status=Notification.NotificationStatus.UNREAD
)

# Mark a notification as read
notification = Notification.objects.get(id=notification_id)
notification.mark_as_read()

# Get notifications by type
reservation_notifications = Notification.objects.filter(
    user=user,
    type=Notification.NotificationType.NEW_RESERVATION
)
```

## Frontend Integration

### 1. WebSocket Connection

```javascript
// Connect to WebSocket
const socket = new WebSocket('ws://yourdomain.com/ws/notifications/');

// Handle connection
socket.onopen = () => {
    console.log('WebSocket connected');
    // Subscribe to specific notification types
    socket.send(JSON.stringify({
        type: 'subscribe',
        notification_types: [
            'new_reservation',
            'reservation_expired',
            'reservation_cancelled',
            'upcoming_reservation'
        ]
    }));
};

// Handle incoming notifications
socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received notification:', data);
    
    // Handle different notification types
    switch(data.type) {
        case 'new_reservation':
            handleNewReservation(data);
            break;
        case 'reservation_expired':
            handleExpiredReservation(data);
            break;
        case 'reservation_cancelled':
            handleCancelledReservation(data);
            break;
        case 'upcoming_reservation':
            handleUpcomingReservation(data);
            break;
    }
};

// Handle disconnection
socket.onclose = () => {
    console.log('WebSocket disconnected');
    // Implement reconnection logic here
};
```

### 2. Notification Data Structure

```javascript
{
    "type": "notification_type",
    "message": "Your message",
    "data": {
        "notification_id": 123,
        "created_at": "2024-03-14T12:00:00Z",
        // Additional data based on notification type
        "reservation_id": 456,
        "parking_lot": "Parking Lot A",
        "start_time": "2024-03-14T13:00:00Z",
        "end_time": "2024-03-14T14:00:00Z"
    }
}
```

## Database Structure

The notification system uses the following database model:

```python
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=50, choices=NotificationType.choices)
    message = models.TextField()
    data = models.JSONField(default=dict)
    status = models.CharField(max_length=10, choices=NotificationStatus.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## WebSocket Events

### 1. Connection
- Endpoint: `ws://yourdomain.com/ws/notifications/`
- Authentication: Uses Django's authentication system
- Headers: Include JWT token in the connection request

### 2. Subscription
```javascript
// Subscribe to notifications
socket.send(JSON.stringify({
    type: 'subscribe',
    notification_types: ['type1', 'type2']
}));
```

### 3. Automatic Notifications
The system automatically sends notifications for:
- New reservations
- Expired reservations
- Cancelled reservations
- Upcoming reservations (30 minutes before start)

### 4. Error Handling
```javascript
socket.onerror = (error) => {
    console.error('WebSocket error:', error);
    // Implement error handling logic
};
```

## Best Practices

1. **Error Handling**
   - Always implement reconnection logic
   - Handle WebSocket errors gracefully
   - Implement fallback mechanisms for offline scenarios

2. **Performance**
   - Use pagination when querying notifications
   - Implement notification cleanup for old records
   - Use appropriate indexes for queries

3. **Security**
   - Always authenticate WebSocket connections
   - Validate notification data
   - Implement rate limiting for notification sending

4. **User Experience**
   - Show notification badges for unread notifications
   - Implement notification grouping
   - Provide clear notification actions

## Example Implementation

```javascript
class NotificationManager {
    constructor() {
        this.socket = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
    }

    connect() {
        this.socket = new WebSocket('ws://yourdomain.com/ws/notifications/');
        this.setupEventHandlers();
    }

    setupEventHandlers() {
        this.socket.onopen = this.handleOpen.bind(this);
        this.socket.onmessage = this.handleMessage.bind(this);
        this.socket.onclose = this.handleClose.bind(this);
        this.socket.onerror = this.handleError.bind(this);
    }

    handleOpen() {
        console.log('Connected to notification service');
        this.reconnectAttempts = 0;
        this.subscribe();
    }

    handleMessage(event) {
        const notification = JSON.parse(event.data);
        this.processNotification(notification);
    }

    handleClose() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            setTimeout(() => {
                this.reconnectAttempts++;
                this.connect();
            }, 1000 * Math.pow(2, this.reconnectAttempts));
        }
    }

    handleError(error) {
        console.error('WebSocket error:', error);
    }

    subscribe() {
        this.socket.send(JSON.stringify({
            type: 'subscribe',
            notification_types: [
                'new_reservation',
                'reservation_expired',
                'reservation_cancelled',
                'upcoming_reservation'
            ]
        }));
    }

    processNotification(notification) {
        // Update UI
        this.updateNotificationBadge();
        this.showNotificationToast(notification);
        this.updateNotificationList(notification);
    }
}
``` 