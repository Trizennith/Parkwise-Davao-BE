# Smart Parking Davao Backend

A Django-based backend system for the Smart Parking Davao application, providing parking management, reservation, and reporting capabilities.

## Features

- User authentication and authorization
- Parking lot management
- Real-time parking space availability
- Reservation system
- Reporting and analytics
- Admin dashboard
- API documentation with Swagger/ReDoc

## Tech Stack

- Python 3.11
- Django 4.2
- Django REST Framework
- PostgreSQL
- JWT Authentication
- Docker
- Swagger/ReDoc for API documentation

## Prerequisites

- Docker and Docker Compose
- Git

## Getting Started

### 1. Clone the repository
```bash
git clone <repository-url>
cd smart-parking-davao/back-end
```

### 2. Environment Setup

Create a `.env` file in the back-end directory with the following variables:
```env
POSTGRES_DB=smart_parking
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432
DEBUG=1
SECRET_KEY=your-secret-key-here
DJANGO_SUPERUSER_PASSWORD=admin123
```

### 3. Run with Docker

```bash
# Build and start the containers
docker-compose up --build

# To run in detached mode
docker-compose up -d --build
```

The application will be available at:
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/swagger/
- Admin Interface: http://localhost:8000/admin/

## API Documentation

### Authentication Endpoints

#### Register a new user
```http
POST /api/accounts/register/
Content-Type: application/json

{
    "email": "user@example.com",
    "username": "user",
    "password": "your_password",
    "first_name": "John",
    "last_name": "Doe"
}
```

Response:
```json
{
    "id": 1,
    "email": "user@example.com",
    "username": "user",
    "first_name": "John",
    "last_name": "Doe",
    "date_joined": "2024-03-20T10:00:00Z"
}
```

#### Login
```http
POST /api/accounts/login/
Content-Type: application/json

{
    "username": "user",
    "password": "your_password"
}
```

Response:
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Refresh Token
```http
POST /api/token/refresh/
Content-Type: application/json

{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

Response:
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### User Management

#### Get User Profile
```http
GET /api/accounts/profile/
Authorization: Bearer your.jwt.token
```

Response:
```json
{
    "id": 1,
    "email": "user@example.com",
    "username": "user",
    "first_name": "John",
    "last_name": "Doe",
    "date_joined": "2024-03-20T10:00:00Z",
    "profile": {
        "phone_number": "+1234567890",
        "address": "123 Main St",
        "role": "user"
    }
}
```

#### Update User Profile
```http
PUT /api/accounts/profile/
Authorization: Bearer your.jwt.token
Content-Type: application/json

{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "profile": {
        "phone_number": "+1234567890",
        "address": "123 Main St"
    }
}
```

Response:
```json
{
    "id": 1,
    "email": "john.doe@example.com",
    "username": "user",
    "first_name": "John",
    "last_name": "Doe",
    "date_joined": "2024-03-20T10:00:00Z",
    "profile": {
        "phone_number": "+1234567890",
        "address": "123 Main St",
        "role": "user"
    }
}
```

#### Change Password
```http
POST /api/accounts/change-password/
Authorization: Bearer your.jwt.token
Content-Type: application/json

{
    "old_password": "current_password",
    "new_password": "new_password"
}
```

Response:
```json
{
    "detail": "Password successfully updated."
}
```

### Parking Management

#### List Parking Lots
```http
GET /api/parking/lots/
Authorization: Bearer your.jwt.token
```

Response:
```json
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "SM City Davao",
            "address": "Quimpo Blvd, Davao City",
            "latitude": "7.073100",
            "longitude": "125.612800",
            "total_spaces": 200,
            "available_spaces": 50,
            "status": "active",
            "hourly_rate": "50.00"
        },
        {
            "id": 2,
            "name": "Abreeza Mall",
            "address": "J.P. Laurel Ave, Davao City",
            "latitude": "7.068200",
            "longitude": "125.608700",
            "total_spaces": 150,
            "available_spaces": 30,
            "status": "active",
            "hourly_rate": "50.00"
        }
    ]
}
```

#### Get Parking Lot Details
```http
GET /api/parking/lots/{id}/
Authorization: Bearer your.jwt.token
```

Response:
```json
{
    "id": 1,
    "name": "SM City Davao",
    "address": "Quimpo Blvd, Davao City",
    "latitude": "7.073100",
    "longitude": "125.612800",
    "total_spaces": 200,
    "available_spaces": 50,
    "status": "active",
    "hourly_rate": "50.00",
    "spaces": [
        {
            "id": 1,
            "space_number": "SMC001",
            "status": "available"
        },
        {
            "id": 2,
            "space_number": "SMC002",
            "status": "reserved"
        }
    ]
}
```

#### Create Reservation
```http
POST /api/reservations/
Authorization: Bearer your.jwt.token
Content-Type: application/json

{
    "parking_lot": 1,
    "parking_space": 1,
    "start_time": "2024-03-20T10:00:00Z",
    "end_time": "2024-03-20T12:00:00Z",
    "vehicle_plate": "ABC123",
    "notes": "Regular parking"
}
```

Response:
```json
{
    "id": 1,
    "parking_lot": {
        "id": 1,
        "name": "SM City Davao"
    },
    "parking_space": {
        "id": 1,
        "space_number": "SMC001"
    },
    "user": {
        "id": 1,
        "username": "user",
        "email": "user@example.com"
    },
    "vehicle_plate": "ABC123",
    "start_time": "2024-03-20T10:00:00Z",
    "end_time": "2024-03-20T12:00:00Z",
    "status": "active",
    "notes": "Regular parking",
    "total_cost": "100.00",
    "created_at": "2024-03-20T09:00:00Z"
}
```

#### List Reservations
```http
GET /api/reservations/
Authorization: Bearer your.jwt.token
```

Response:
```json
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "parking_lot": {
                "id": 1,
                "name": "SM City Davao"
            },
            "parking_space": {
                "id": 1,
                "space_number": "SMC001"
            },
            "start_time": "2024-03-20T10:00:00Z",
            "end_time": "2024-03-20T12:00:00Z",
            "status": "active",
            "total_cost": "100.00"
        },
        {
            "id": 2,
            "parking_lot": {
                "id": 2,
                "name": "Abreeza Mall"
            },
            "parking_space": {
                "id": 3,
                "space_number": "ABR001"
            },
            "start_time": "2024-03-21T14:00:00Z",
            "end_time": "2024-03-21T16:00:00Z",
            "status": "active",
            "total_cost": "100.00"
        }
    ]
}
```

#### Cancel Reservation
```http
PATCH /api/reservations/{id}/cancel/
Authorization: Bearer your.jwt.token
```

Response:
```json
{
    "id": 1,
    "status": "cancelled",
    "cancelled_at": "2024-03-20T09:30:00Z"
}
```

## Development

### Local Development Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Create a superuser:
```bash
python manage.py createsuperuser
```

5. Run the development server:
```bash
python manage.py runserver
```

### Running Tests
```bash
python manage.py test
```

## Project Structure

```
back-end/
├── apps/
│   ├── accounts/         # User management
│   ├── parking_lots/     # Parking lot management
│   ├── reservations/     # Reservation system
│   ├── reports/         # Reporting and analytics
│   └── jwt_blacklist/   # JWT token management
├── smart_parking/       # Project settings
├── manage.py
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, email support@smartparkingdavao.com or create an issue in the repository. 