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
- Advanced notification system with real-time updates
- Comprehensive reporting with data validation
- Role-based access control
- Automated deployment with GitHub Actions

## Tech Stack

- Django 5.0.2
- Django REST Framework 3.14.0
- Channels 4.0.0 (WebSocket)
- PostgreSQL 14+
- Redis 7+
- JWT Authentication
- Docker & Docker Swarm
- Traefik (Reverse Proxy)
- GitHub Container Registry (ghcr.io)

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
# Install pipenv if you don't have it
pip install pipenv

# Install dependencies using Pipenv
pipenv install

# Activate the virtual environment
pipenv shell

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run migrations
pipenv run python manage.py migrate

# Create superuser
pipenv run python manage.py createsuperuser

# Run development server
pipenv run python manage.py runserver
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
- `notification`: Real-time notifications for:
  - New reservations
  - Expired reservations
  - Cancelled reservations
  - Upcoming reservations (30 minutes before start)

## API Endpoints

### Authentication

#### Register User
```http
POST /api/auth/register/
```
Request:
```json
{
    "email": "user@example.com",
    "password": "securepassword123",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+639123456789"
}
```
Response:
```json
{
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+639123456789",
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Login
```http
POST /api/auth/login/
```
Request:
```json
{
    "email": "user@example.com",
    "password": "securepassword123"
}
```
Response:
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### User Management
- `GET /api/users/`: List all users (admin only)
- `GET /api/users/{id}/`: Get user details (admin only)
- `PUT /api/users/{id}/`: Update user (admin only)
- `DELETE /api/users/{id}/`: Delete user (admin only)
- `GET /api/users/me/`: Get current user profile
- `GET /api/profile/`: Get user profile
- `PATCH /api/profile/`: Update user profile

### Parking Lots

#### Create Parking Lot (Admin Only)
```http
POST /api/parking-lots/
```
Request:
```json
{
    "name": "SM City Davao Parking",
    "address": "Quimpo Blvd, Davao City",
    "latitude": 7.0731,
    "longitude": 125.6128,
    "total_spaces": 100,
    "hourly_rate": 50.00,
    "status": "active"
}
```
Response:
```json
{
    "id": 1,
    "name": "SM City Davao Parking",
    "address": "Quimpo Blvd, Davao City",
    "latitude": 7.0731,
    "longitude": 125.6128,
    "total_spaces": 100,
    "available_spaces": 100,
    "hourly_rate": "50.00",
    "status": "active",
    "created_at": "2024-03-15T08:00:00Z",
    "updated_at": "2024-03-15T08:00:00Z"
}
```

- `GET /api/parking-lots/`: List parking lots
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

#### Create Reservation
```http
POST /api/reservations/
```
Request:
```json
{
    "parking_lot": 1,
    "parking_space": "A001",
    "vehicle_plate": "ABC123",
    "start_time": "2024-03-15T10:00:00Z",
    "end_time": "2024-03-15T12:00:00Z",
    "notes": "Near entrance"
}
```
Response:
```json
{
    "id": 1,
    "parking_lot": 1,
    "parking_lot_name": "SM City Davao Parking",
    "parking_space": {
        "id": 1,
        "space_number": "A001",
        "status": "reserved"
    },
    "user": {
        "id": 1,
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe"
    },
    "vehicle_plate": "ABC123",
    "notes": "Near entrance",
    "start_time": "2024-03-15T10:00:00Z",
    "end_time": "2024-03-15T12:00:00Z",
    "status": "active",
    "duration": 2.0,
    "total_cost": "100.00",
    "created_at": "2024-03-15T09:00:00Z",
    "updated_at": "2024-03-15T09:00:00Z"
}
```

- `GET /api/reservations/`: List reservations
- `GET /api/reservations/{id}/`: Get reservation details
- `PUT /api/reservations/{id}/`: Update reservation
- `DELETE /api/reservations/{id}/`: Cancel reservation
- `GET /api/reservations/my/`: Get current user's reservations
- `GET /api/reservations/active/`: Get active reservations
- `POST /api/reservations/{id}/cancel/`: Cancel a reservation
- `PATCH /api/reservations/{id}/status/`: Update reservation status (admin only)

### Notifications

#### Create Notification
```http
POST /api/notifications/
```
Request:
```json
{
    "type": "new_reservation",
    "message": "Your reservation for parking space A001 has been confirmed",
    "data": {
        "reservation_id": 1,
        "parking_lot": "SM City Davao Parking",
        "start_time": "2024-03-15T10:00:00Z"
    }
}
```
Response:
```json
{
    "id": 1,
    "type": "new_reservation",
    "message": "Your reservation for parking space A001 has been confirmed",
    "data": {
        "reservation_id": 1,
        "parking_lot": "SM City Davao Parking",
        "start_time": "2024-03-15T10:00:00Z"
    },
    "status": "unread",
    "created_at": "2024-03-15T09:00:00Z",
    "updated_at": "2024-03-15T09:00:00Z"
}
```

- `GET /api/notifications/`: List user notifications
- `DELETE /api/notifications/{id}/`: Delete a notification
- `POST /api/notifications/{id}/mark-as-read/`: Mark notification as read
- `POST /api/notifications/mark-all-as-read/`: Mark all notifications as read
- `DELETE /api/notifications/delete-all/`: Delete all notifications
- `GET /api/notifications/unread-count/`: Get count of unread notifications

### Reports

#### Get Daily Report
```http
GET /api/reports/daily/?date=2024-03-15
```
Response:
```json
{
    "date": "2024-03-15",
    "total_revenue": "5000.00",
    "total_reservations": 50,
    "occupancy_rate": 75.5,
    "average_duration": 2.5,
    "peak_hour": "14:00:00",
    "parking_lot_stats": [
        {
            "parking_lot_id": 1,
            "parking_lot_name": "SM City Davao Parking",
            "revenue": "3000.00",
            "reservations": 30,
            "occupancy_rate": 80.0
        }
    ]
}
```

#### Get Report Summary
```http
GET /api/reports/summary/
```
Response:
```json
{
    "total_revenue": "5000.00",
    "daily_reservations": 50,
    "parking_utilization": 75.5,
    "average_duration": 2.5,
    "revenue_change": 500.00,
    "reservation_change": 5,
    "utilization_change": 2.5,
    "duration_change": 0.5
}
```

- `GET /api/reports/monthly/`: Get monthly reports
- `GET /api/reports/parking-lot/{id}/`: Get parking lot specific reports
- `GET /api/reports/export/`: Export reports (CSV)

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
- Secure WebSocket connections
- Data validation for reports and statistics

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Production Deployment

For production deployment instructions, see the [Docker Deployment Guide](docker/README.md).

### GitHub Container Registry Setup

1. Create a GitHub Personal Access Token (PAT) with `write:packages` scope
2. Login to GitHub Container Registry:
```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
```

3. Build and push the image:
```bash
docker build -t ghcr.io/YOUR_GITHUB_USERNAME/parkwise-davao-app:latest .
docker push ghcr.io/YOUR_GITHUB_USERNAME/parkwise-davao-app:latest
```

4. Deploy using Docker Swarm:
```bash
docker stack deploy -c docker/app.deploy.yml parkwise
```

## CI/CD Pipeline

The project uses GitHub Actions for continuous integration and deployment:

- Automated testing on pull requests
- Docker image building and pushing
- Automated deployment to staging/production
- Security scanning
- Code quality checks

For more details, see the workflow files in `.github/workflows/`.
