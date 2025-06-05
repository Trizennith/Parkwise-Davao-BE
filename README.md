# ParkWise Davao Backend

The backend service for ParkWise Davao, a smart parking management system providing real-time parking space availability, reservations, and automated payment processing.

## Features

- Real-time parking space monitoring
- WebSocket-based notifications
- JWT Authentication
- RESTful API
- Admin dashboard
- Database management
- Payment processing
- Report generation

## Tech Stack

- Django 5.0.2
- Django REST Framework 3.14.0
- Channels 4.0.0 (WebSocket)
- PostgreSQL 14+
- Redis 7+
- JWT Authentication
- Docker & Docker Swarm
- Traefik (Reverse Proxy)

## Prerequisites

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 14+
- Redis 7+

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/Trizennith/Parkwise-Davao-BE.git
cd Parkwise-Davao-BE
```

2. Set up the development environment:
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

## Docker Development

1. Local Development (with local database):
```bash
docker-compose -f docker/app.local.db.yml up --build
```

2. Local Development (with containerized database):
```bash
docker-compose -f docker/app.local.yml up --build
```

3. Access the services:
- API: http://localhost:8011
- Admin Interface: http://localhost:8011/admin
- API Documentation: http://localhost:8011/api/docs/

## Testing

Run the test suite using Docker:
```bash
# Run all tests
./scripts/run_tests.sh

# Or manually using Docker Compose
docker-compose -f docker/app.test.yml up --build
```

## Project Structure

```
back-end/
├── app/
│   ├── api/               # API endpoints
│   │   ├── accounts/     # User management
│   │   ├── parking_lots/ # Parking lot management
│   │   ├── reservations/ # Reservation system
│   │   ├── reports/      # Report generation
│   │   ├── jwt_blacklist/# JWT token management
│   │   ├── notification/ # Notification system
│   │   └── realtime/     # WebSocket handling
│   ├── config/           # Django settings
│   ├── test/            # Test modules
│   │   ├── accounts/    # Account tests
│   │   ├── parking_lots/# Parking lot tests
│   │   ├── reservations/# Reservation tests
│   │   └── reports/     # Report tests
│   └── utils/           # Utility functions
├── docker/              # Docker configuration
│   ├── app.local.yml   # Local development compose file
│   ├── app.local.db.yml# Local development with local DB
│   ├── app.test.yml    # Test environment compose file
│   ├── app.deploy.yml  # Production compose file
│   └── traefik.yml     # Traefik configuration
├── scripts/            # Utility scripts
│   └── run_tests.sh   # Test runner script
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Environment Variables

The application uses environment variables for configuration. You can set these up in two ways:

1. Using a `.env` file (recommended for local development):
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit the .env file with your settings
   nano .env
   ```

2. Setting environment variables directly (recommended for production):
   ```bash
   export DJANGO_SECRET_KEY=your-secret-key
   export DJANGO_DEBUG=False
   # ... etc
   ```

### Required Environment Variables

```env
# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_CORS_ALLOWED_ORIGINS=http://localhost:5173

# Database Settings
POSTGRES_DB=parkwise_davao
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Redis Settings
REDIS_HOST=localhost
REDIS_PORT=6379

# Channel Layers Settings
CHANNEL_LAYERS_REDIS_HOST=localhost
CHANNEL_LAYERS_REDIS_PORT=6379
```

### Environment Variables in Different Environments

- **Local Development**: Use `.env` file
- **Testing**: Environment variables are set in GitHub Actions workflow
- **Staging/Production**: Environment variables are set in Docker Compose files

## API Documentation

- Swagger UI: http://localhost:8011/api/docs/
- ReDoc: http://localhost:8011/api/redoc/

## WebSocket Events

The system uses WebSocket for real-time updates. Available events:

- `parking_space_update`: Updates when parking space status changes
- `reservation_update`: Updates when reservation status changes
- `payment_update`: Updates when payment status changes

## API Endpoints

### Authentication
- `POST /api/auth/register/`: User registration
- `POST /api/auth/login/`: User login
- `POST /api/auth/refresh-token/`: Refresh JWT token
- `POST /api/auth/change-password/`: Change user password
- `POST /api/auth/token/ws/`: Get WebSocket token
- `POST /api/auth/logout/`: Logout user and blacklist token

### User Management
- `GET /api/users/`: List all users (admin only)
- `GET /api/users/{id}/`: Get user details (admin only)
- `PUT /api/users/{id}/`: Update user (admin only)
- `DELETE /api/users/{id}/`: Delete user (admin only)
- `GET /api/users/me/`: Get current user profile
- `GET /api/profile/`: Get user profile
- `PATCH /api/profile/`: Update user profile

### Parking Lots
- `GET /api/parking-lots/`: List parking lots
- `POST /api/parking-lots/`: Create parking lot (admin only)
- `GET /api/parking-lots/{id}/`: Get parking lot details
- `PUT /api/parking-lots/{id}/`: Update parking lot (admin only)
- `DELETE /api/parking-lots/{id}/`: Delete parking lot (admin only)
- `GET /api/parking-lots/{id}/occupancy-rate/`: Get parking lot occupancy rate
- `GET /api/parking-lots/search/`: Search parking lots by name or address
- `GET /api/parking-lots/active/`: Get all active parking lots

### Parking Spaces
- `GET /api/parking-spaces/`: List parking spaces
- `POST /api/parking-spaces/`: Create parking space (admin only)
- `GET /api/parking-spaces/{id}/`: Get parking space details
- `PUT /api/parking-spaces/{id}/`: Update parking space (admin only)
- `DELETE /api/parking-spaces/{id}/`: Delete parking space (admin only)
- `POST /api/parking-spaces/{id}/reserve/`: Reserve a parking space
- `POST /api/parking-spaces/{id}/occupy/`: Occupy a parking space
- `POST /api/parking-spaces/{id}/vacate/`: Vacate a parking space

### Reservations
- `GET /api/reservations/`: List reservations
- `POST /api/reservations/`: Create reservation
- `GET /api/reservations/{id}/`: Get reservation details
- `PUT /api/reservations/{id}/`: Update reservation
- `DELETE /api/reservations/{id}/`: Cancel reservation
- `GET /api/reservations/my/`: Get current user's reservations
- `GET /api/reservations/active/`: Get active reservations
- `POST /api/reservations/{id}/cancel/`: Cancel a reservation
- `PATCH /api/reservations/{id}/status/`: Update reservation status (admin only)

### Notifications
- `GET /api/notifications/`: List user notifications
- `DELETE /api/notifications/{id}/`: Delete a notification
- `POST /api/notifications/{id}/mark-as-read/`: Mark notification as read
- `POST /api/notifications/mark-all-as-read/`: Mark all notifications as read
- `DELETE /api/notifications/delete-all/`: Delete all notifications
- `GET /api/notifications/unread-count/`: Get count of unread notifications

### Reports
- `GET /api/reports/daily/`: Get daily reports
- `GET /api/reports/monthly/`: Get monthly reports
- `GET /api/reports/parking-lot/{id}/`: Get parking lot specific reports
- `GET /api/reports/export/`: Export reports (CSV)
- `GET /api/reports/summary/`: Get report summary

## Security

- JWT Authentication for all API endpoints
- WebSocket authentication with short-lived tokens
- CORS configuration
- SQL injection protection
- XSS protection
- CSRF protection
- Rate limiting
- Input validation
- Password hashing and validation
- Role-based access control

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Production Deployment

For production deployment instructions, see the [Docker Deployment Guide](docker/README.md).
