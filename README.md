# Smart Parking Davao Backend

A Django-based backend system for the Smart Parking Davao application, providing parking management, reservation, and reporting capabilities.

## Features

- User authentication and authorization
- Parking lot management
- Real-time parking space availability
- Reservation system
- Comprehensive reporting and analytics
  - Daily reports
  - Monthly reports
  - Parking lot specific reports
  - Custom date range reports
  - CSV export functionality
- Admin dashboard
- API documentation with Swagger/ReDoc

## Tech Stack

- Python 3.11
- Django 5.0.2
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
- API Documentation: http://localhost:8000/swagger
- Admin Interface: http://localhost:8000/admin

## API Documentation

### Authentication Endpoints

#### Register a new user
```http
POST /auth/register
Content-Type: application/json

{
    "email": "user@example.com",
    "username": "user",
    "password": "your_password",
    "password2": "your_password",
    "first_name": "John",
    "last_name": "Doe",
    "role": "user"
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
    "role": "user",
    "status": "active",
    "avatar_url": null,
    "created_at": "2024-03-20T10:00:00Z",
    "updated_at": "2024-03-20T10:00:00Z"
}
```

#### Login
```http
POST /auth/login
Content-Type: application/json

{
    "email": "user@example.com",
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
POST /auth/refresh-token
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

#### Change Password
```http
POST /auth/change-password
Authorization: Bearer your.jwt.token
Content-Type: application/json

{
    "old_password": "current_password",
    "new_password": "new_password",
    "new_password2": "new_password"
}
```

Response:
```json
{
    "detail": "Password successfully updated."
}
```

### User Endpoints

#### Get User Profile
```http
GET /auth/profile
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
    "role": "user",
    "status": "active",
    "avatar_url": null,
    "created_at": "2024-03-20T10:00:00Z",
    "updated_at": "2024-03-20T10:00:00Z"
}
```

#### Update User Profile
```http
PUT /auth/profile
Authorization: Bearer your.jwt.token
Content-Type: application/json

{
    "first_name": "John",
    "last_name": "Doe",
    "avatar_url": "https://example.com/avatar.jpg"
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
    "role": "user",
    "status": "active",
    "avatar_url": "https://example.com/avatar.jpg",
    "created_at": "2024-03-20T10:00:00Z",
    "updated_at": "2024-03-20T10:00:00Z"
}
```

### Admin Endpoints

#### User Management

##### List All Users
```http
GET /admin-api/users
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
            "email": "user@example.com",
            "username": "user",
            "first_name": "John",
            "last_name": "Doe",
            "role": "user",
            "status": "active",
            "avatar_url": null,
            "created_at": "2024-03-20T10:00:00Z",
            "updated_at": "2024-03-20T10:00:00Z"
        }
    ]
}
```

##### Get User Details
```http
GET /admin-api/users/{user_id}
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
    "role": "user",
    "status": "active",
    "avatar_url": null,
    "created_at": "2024-03-20T10:00:00Z",
    "updated_at": "2024-03-20T10:00:00Z"
}
```

#### Parking Lot Management

##### List Parking Lots
```http
GET /admin-api/parking-lots
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
        }
    ]
}
```

##### Update Parking Lot Status
```http
PATCH /admin-api/parking-lots/{id}/status
Authorization: Bearer your.jwt.token
Content-Type: application/json

{
    "status": "maintenance"
}
```

##### Manage Parking Spaces
```http
GET /admin-api/parking-lots/{id}/spaces
POST /admin-api/parking-lots/{id}/spaces
PATCH /admin-api/parking-lots/{id}/spaces/{space_id}
DELETE /admin-api/parking-lots/{id}/spaces/{space_id}
Authorization: Bearer your.jwt.token
```

#### Reservation Management

##### List All Reservations
```http
GET /admin-api/reservations
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
            "user": {
                "id": 1,
                "email": "user@example.com",
                "username": "user",
                "first_name": "John",
                "last_name": "Doe"
            },
            "parking_lot": {
                "id": 1,
                "name": "SM City Davao",
                "address": "Quimpo Blvd, Davao City"
            },
            "parking_space": {
                "id": 1,
                "space_number": "A-001",
                "type": "standard"
            },
            "start_time": "2024-03-20T10:00:00Z",
            "end_time": "2024-03-20T12:00:00Z",
            "status": "active",
            "vehicle_plate": "ABC123",
            "notes": "Regular parking",
            "created_at": "2024-03-20T09:00:00Z",
            "updated_at": "2024-03-20T09:00:00Z"
        }
    ]
}
```

##### Update Reservation Status
```http
PATCH /admin-api/reservations/{id}/status
Authorization: Bearer your.jwt.token
Content-Type: application/json

{
    "status": "completed"
}
```

Response:
```json
{
    "id": 1,
    "user": {
        "id": 1,
        "email": "user@example.com",
        "username": "user",
        "first_name": "John",
        "last_name": "Doe"
    },
    "parking_lot": {
        "id": 1,
        "name": "SM City Davao",
        "address": "Quimpo Blvd, Davao City"
    },
    "parking_space": {
        "id": 1,
        "space_number": "A-001",
        "type": "standard"
    },
    "start_time": "2024-03-20T10:00:00Z",
    "end_time": "2024-03-20T12:00:00Z",
    "status": "completed",
    "vehicle_plate": "ABC123",
    "notes": "Regular parking",
    "created_at": "2024-03-20T09:00:00Z",
    "updated_at": "2024-03-20T12:00:00Z"
}
```

#### Payment Management

##### List All Payments
```http
GET /admin-api/payments
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
            "reservation": {
                "id": 1,
                "user": {
                    "id": 1,
                    "email": "user@example.com",
                    "username": "user"
                },
                "parking_lot": {
                    "id": 1,
                    "name": "SM City Davao"
                },
                "parking_space": {
                    "id": 1,
                    "space_number": "A-001"
                },
                "start_time": "2024-03-20T10:00:00Z",
                "end_time": "2024-03-20T12:00:00Z"
            },
            "amount": 100.00,
            "payment_method": "credit_card",
            "status": "paid",
            "transaction_id": "txn_123456789",
            "created_at": "2024-03-20T09:30:00Z",
            "updated_at": "2024-03-20T09:30:00Z"
        }
    ]
}
```

##### Update Payment Status
```http
PATCH /admin-api/payments/{id}/status
Authorization: Bearer your.jwt.token
Content-Type: application/json

{
    "status": "paid"
}
```

Response:
```json
{
    "id": 1,
    "reservation": {
        "id": 1,
        "user": {
            "id": 1,
            "email": "user@example.com",
            "username": "user"
        },
        "parking_lot": {
            "id": 1,
            "name": "SM City Davao"
        },
        "parking_space": {
            "id": 1,
            "space_number": "A-001"
        },
        "start_time": "2024-03-20T10:00:00Z",
        "end_time": "2024-03-20T12:00:00Z"
    },
    "amount": 100.00,
    "payment_method": "credit_card",
    "status": "paid",
    "transaction_id": "txn_123456789",
    "created_at": "2024-03-20T09:30:00Z",
    "updated_at": "2024-03-20T09:35:00Z"
}
```

#### Reports

##### Get Daily Summary
```http
GET /admin-api/reports/summary
Authorization: Bearer your.jwt.token
```

Response:
```json
{
    "total_revenue": 15000.00,
    "total_reservations": 50,
    "total_parking_spaces": 200,
    "available_spaces": 150,
    "occupied_spaces": 50,
    "date": "2024-03-20"
}
```

##### Get Monthly Report
```http
GET /admin-api/reports/monthly
Authorization: Bearer your.jwt.token
```

Response:
```json
{
    "month": 3,
    "year": 2024,
    "total_revenue": 450000.00,
    "total_reservations": 1500,
    "average_daily_revenue": 15000.00,
    "average_daily_reservations": 50,
    "peak_usage_day": "2024-03-15",
    "peak_usage_count": 75
}
```

##### Get Date Range Report
```http
GET /admin-api/reports/date-range?start_date=2024-03-01&end_date=2024-03-31
Authorization: Bearer your.jwt.token
```

Response:
```json
{
    "start_date": "2024-03-01",
    "end_date": "2024-03-31",
    "total_revenue": 450000.00,
    "total_reservations": 1500,
    "daily_averages": {
        "revenue": 15000.00,
        "reservations": 50
    },
    "parking_lot_breakdown": [
        {
            "parking_lot_id": 1,
            "name": "SM City Davao",
            "total_revenue": 225000.00,
            "total_reservations": 750
        }
    ]
}
```

##### Get Parking Lot Report
```http
GET /admin-api/reports/parking-lot/{id}
Authorization: Bearer your.jwt.token
```

Response:
```json
{
    "parking_lot": {
        "id": 1,
        "name": "SM City Davao",
        "address": "Quimpo Blvd, Davao City"
    },
    "total_revenue": 225000.00,
    "total_reservations": 750,
    "space_utilization": {
        "total_spaces": 200,
        "average_occupancy_rate": 75.5,
        "peak_occupancy_rate": 90.0,
        "peak_occupancy_date": "2024-03-15"
    },
    "monthly_breakdown": [
        {
            "month": 3,
            "year": 2024,
            "revenue": 225000.00,
            "reservations": 750
        }
    ]
}
```

##### Export Report
```http
GET /admin-api/reports/export?type=daily&start_date=2024-03-01&end_date=2024-03-31
Authorization: Bearer your.jwt.token
```

Response:
```
Content-Type: text/csv
Content-Disposition: attachment; filename="daily_report_2024-03.csv"

Date,Total Revenue,Total Reservations,Available Spaces,Occupied Spaces
2024-03-01,15000.00,50,150,50
2024-03-02,16000.00,55,145,55
...
```

### User Reservation Endpoints

#### List My Reservations
```http
GET /user/reservations
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
                "name": "SM City Davao",
                "address": "Quimpo Blvd, Davao City"
            },
            "parking_space": {
                "id": 1,
                "space_number": "A-001",
                "type": "standard"
            },
            "start_time": "2024-03-20T10:00:00Z",
            "end_time": "2024-03-20T12:00:00Z",
            "status": "active",
            "vehicle_plate": "ABC123",
            "notes": "Regular parking",
            "created_at": "2024-03-20T09:00:00Z",
            "updated_at": "2024-03-20T09:00:00Z"
        }
    ]
}
```

#### Create Reservation
```http
POST /user/reservations
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
        "name": "SM City Davao",
        "address": "Quimpo Blvd, Davao City"
    },
    "parking_space": {
        "id": 1,
        "space_number": "A-001",
        "type": "standard"
    },
    "start_time": "2024-03-20T10:00:00Z",
    "end_time": "2024-03-20T12:00:00Z",
    "status": "active",
    "vehicle_plate": "ABC123",
    "notes": "Regular parking",
    "created_at": "2024-03-20T09:00:00Z",
    "updated_at": "2024-03-20T09:00:00Z"
}
```

#### Cancel Reservation
```http
POST /user/reservations/{id}/cancel
Authorization: Bearer your.jwt.token
```

Response:
```json
{
    "id": 1,
    "parking_lot": {
        "id": 1,
        "name": "SM City Davao",
        "address": "Quimpo Blvd, Davao City"
    },
    "parking_space": {
        "id": 1,
        "space_number": "A-001",
        "type": "standard"
    },
    "start_time": "2024-03-20T10:00:00Z",
    "end_time": "2024-03-20T12:00:00Z",
    "status": "cancelled",
    "vehicle_plate": "ABC123",
    "notes": "Regular parking",
    "created_at": "2024-03-20T09:00:00Z",
    "updated_at": "2024-03-20T09:05:00Z"
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
    "detail": "Invalid input data",
    "errors": {
        "field_name": ["Error message"]
    }
}
```

### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
    "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
    "detail": "Not found."
}
```

### 500 Internal Server Error
```json
{
    "detail": "Internal server error."
}
```

## Development

### Running Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.accounts
```

### Code Style
This project follows PEP 8 style guide. To check your code style:
```bash
flake8
```

### Database Migrations
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
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

# Smart Parking Davao API Documentation

## API Endpoints

### Authentication
```
POST /api/auth/login/
  - Login with email and password
  - Request body: { "email": "user@example.com", "password": "password" }
  - Returns: JWT token and user data

POST /api/auth/refresh-token/
  - Refresh JWT token
  - Request body: { "refresh": "your_refresh_token" }
  - Returns: New access token

POST /api/auth/register/
  - Register new user
  - Request body: { "email": "user@example.com", "password": "password", "first_name": "John", "last_name": "Doe" }
```

### User Endpoints
```
GET /api/user/profile/
  - Get current user's profile
  - Requires authentication

PUT /api/user/profile/
  - Update current user's profile
  - Requires authentication

POST /api/user/change-password/
  - Change user password
  - Requires authentication
  - Request body: { "old_password": "old", "new_password": "new" }
```

### Admin API Endpoints
```
# Users Management
GET /api/admin/users/
  - List all users (admin only)
  - Requires admin authentication

GET /api/admin/users/{id}/
  - Get user details (admin only)
  - Requires admin authentication

PUT /api/admin/users/{id}/
  - Update user (admin only)
  - Requires admin authentication

DELETE /api/admin/users/{id}/
  - Delete user (admin only)
  - Requires admin authentication

# Parking Lots Management
GET /api/admin/parking-lots/
  - List all parking lots
  - Query params: status, min_spaces, min_rate, max_rate, max_occupancy, search, sort_by
  - Requires admin authentication

POST /api/admin/parking-lots/
  - Create new parking lot (admin only)
  - Requires admin authentication

GET /api/admin/parking-lots/{id}/
  - Get parking lot details
  - Requires admin authentication

PUT /api/admin/parking-lots/{id}/
  - Update parking lot (admin only)
  - Requires admin authentication

DELETE /api/admin/parking-lots/{id}/
  - Delete parking lot (admin only)
  - Requires admin authentication

# Parking Spaces Management
GET /api/admin/spaces/
  - List all parking spaces
  - Query params: lot_id
  - Requires admin authentication

POST /api/admin/spaces/
  - Create new parking space (admin only)
  - Requires admin authentication

GET /api/admin/spaces/{id}/
  - Get parking space details
  - Requires admin authentication

PUT /api/admin/spaces/{id}/
  - Update parking space (admin only)
  - Requires admin authentication

DELETE /api/admin/spaces/{id}/
  - Delete parking space (admin only)
  - Requires admin authentication

# Parking Space Actions
POST /api/admin/spaces/{id}/reserve/
  - Reserve a parking space
  - Requires admin authentication

POST /api/admin/spaces/{id}/occupy/
  - Mark space as occupied
  - Requires admin authentication

POST /api/admin/spaces/{id}/vacate/
  - Mark space as available
  - Requires admin authentication

# Parking Lot Actions
GET /api/admin/parking-lots/{id}/available-spaces/
  - Get available spaces in a parking lot
  - Requires admin authentication

GET /api/admin/parking-lots/{id}/occupancy-rate/
  - Get parking lot occupancy rate
  - Requires admin authentication

GET /api/admin/parking-lots/search/
  - Search parking lots
  - Query params: q (search term)
  - Requires admin authentication

GET /api/admin/parking-lots/active/
  - Get all active parking lots
  - Requires admin authentication

GET /api/admin/parking-lots/with-available-spaces/
  - Get parking lots with available spaces
  - Query params: min_spaces
  - Requires admin authentication
```

### Reports API Endpoints
```
GET /api/admin/reports/summary/
  - Get parking system summary
  - Requires admin authentication

GET /api/admin/reports/daily/
  - Get daily parking reports
  - Query params: date
  - Requires admin authentication

GET /api/admin/reports/monthly/
  - Get monthly parking reports
  - Query params: year, month
  - Requires admin authentication
```

## Authentication

All API endpoints (except login and register) require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer your_jwt_token
```

## Development Setup

1. Clone the repository
2. Create and activate virtual environment
3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create superuser:
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

## Database Seeding

To seed the database with sample data:
```bash
python manage.py seed_data
```

This will create:
- Admin user (email: admin@example.com, password: admin123)
- Regular users
- Sample parking lots
- Sample parking spaces
- Sample reservations

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `/swagger/`
- ReDoc: `/redoc/`

### Parking Space Management

#### List Parking Spaces
```http
GET /admin-api/parking-lots/{id}/spaces
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
            "space_number": "A-001",
            "status": "available",
            "type": "standard",
            "is_reserved": false,
            "parking_lot": 1,
            "created_at": "2024-03-20T10:00:00Z",
            "updated_at": "2024-03-20T10:00:00Z"
        }
    ]
}
```

#### Create Parking Space
```http
POST /admin-api/parking-lots/{id}/spaces
Authorization: Bearer your.jwt.token
Content-Type: application/json

{
    "space_number": "A-002",
    "type": "standard",
    "status": "available"
}
```

Response:
```json
{
    "id": 2,
    "space_number": "A-002",
    "status": "available",
    "type": "standard",
    "is_reserved": false,
    "parking_lot": 1,
    "created_at": "2024-03-20T10:00:00Z",
    "updated_at": "2024-03-20T10:00:00Z"
}
```

#### Update Parking Space
```http
PATCH /admin-api/parking-lots/{id}/spaces/{space_id}
Authorization: Bearer your.jwt.token
Content-Type: application/json

{
    "status": "maintenance",
    "type": "handicapped"
}
```

Response:
```json
{
    "id": 1,
    "space_number": "A-001",
    "status": "maintenance",
    "type": "handicapped",
    "is_reserved": false,
    "parking_lot": 1,
    "created_at": "2024-03-20T10:00:00Z",
    "updated_at": "2024-03-20T10:00:00Z"
}
```

#### Delete Parking Space
```http
DELETE /admin-api/parking-lots/{id}/spaces/{space_id}
Authorization: Bearer your.jwt.token
```

Response:
```json
{
    "detail": "Parking space successfully deleted."
}
```

### Reports

#### Get Daily Summary
```http
GET /reports/summary
Authorization: Bearer your.jwt.token
```

Response:
```json
{
    "total_revenue": 15000.00,
    "total_reservations": 50,
    "total_parking_spaces": 200,
    "available_spaces": 150,
    "occupied_spaces": 50,
    "date": "2024-03-20"
}
```

#### Get Monthly Report
```http
GET /reports/monthly?month=3&year=2024
Authorization: Bearer your.jwt.token
```

Response:
```json
{
    "month": 3,
    "year": 2024,
    "total_revenue": 450000.00,
    "total_reservations": 1500,
    "average_daily_revenue": 15000.00,
    "average_daily_reservations": 50,
    "peak_usage_day": "2024-03-15",
    "peak_usage_count": 75
}
```

#### Get Daily Report
```http
GET /reports/daily?date=2024-03-20
Authorization: Bearer your.jwt.token
```

Response:
```json
{
    "date": "2024-03-20",
    "total_revenue": 15000.00,
    "total_reservations": 50,
    "hourly_breakdown": [
        {
            "hour": 9,
            "reservations": 10,
            "revenue": 3000.00
        }
    ],
    "parking_lot_breakdown": [
        {
            "parking_lot_id": 1,
            "name": "SM City Davao",
            "reservations": 25,
            "revenue": 7500.00
        }
    ]
}
```

#### Get Date Range Report
```http
GET /reports/date-range?start_date=2024-03-01&end_date=2024-03-31
Authorization: Bearer your.jwt.token
```

Response:
```json
{
    "start_date": "2024-03-01",
    "end_date": "2024-03-31",
    "total_revenue": 450000.00,
    "total_reservations": 1500,
    "daily_averages": {
        "revenue": 15000.00,
        "reservations": 50
    },
    "parking_lot_breakdown": [
        {
            "parking_lot_id": 1,
            "name": "SM City Davao",
            "total_revenue": 225000.00,
            "total_reservations": 750
        }
    ]
}
```

#### Get Parking Lot Report
```http
GET /reports/parking-lot/1
Authorization: Bearer your.jwt.token
```

Response:
```json
{
    "parking_lot": {
        "id": 1,
        "name": "SM City Davao",
        "address": "Quimpo Blvd, Davao City"
    },
    "total_revenue": 225000.00,
    "total_reservations": 750,
    "space_utilization": {
        "total_spaces": 200,
        "average_occupancy_rate": 75.5,
        "peak_occupancy_rate": 90.0,
        "peak_occupancy_date": "2024-03-15"
    },
    "monthly_breakdown": [
        {
            "month": 3,
            "year": 2024,
            "revenue": 225000.00,
            "reservations": 750
        }
    ]
}
```

#### Export Report
```http
GET /reports/export?type=daily&start_date=2024-03-01&end_date=2024-03-31
Authorization: Bearer your.jwt.token
```

Response:
```
Content-Type: text/csv
Content-Disposition: attachment; filename="daily_report_2024-03.csv"

Date,Total Revenue,Total Reservations,Available Spaces,Occupied Spaces
2024-03-01,15000.00,50,150,50
2024-03-02,16000.00,55,145,55
...
``` 