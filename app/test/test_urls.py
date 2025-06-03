from django.test import TestCase
from django.urls import reverse, resolve
from app.api.accounts.views import (
    UserRegistrationView,
    UserLoginView,
    UserProfileView,
    ChangePasswordView,
    UserViewSet
)
from app.api.parking_lots.views import (
    ParkingLotViewSet,
    ParkingSpaceViewSet
)
from app.api.reservations.views import ReservationViewSet

class UrlsTestCase(TestCase):
    """Test cases for URL configuration"""

    def test_accounts_urls(self):
        """Test accounts app URLs"""
        # Registration
        url = reverse('user-register')
        self.assertEqual(resolve(url).func.view_class, UserRegistrationView)

        # Login
        url = reverse('user-login')
        self.assertEqual(resolve(url).func.view_class, UserLoginView)

        # Profile
        url = reverse('user-profile')
        self.assertEqual(resolve(url).func.view_class, UserProfileView)

        # Change Password
        url = reverse('user-change-password')
        self.assertEqual(resolve(url).func.view_class, ChangePasswordView)

        # User List/Detail (ViewSet)
        url = reverse('user-list')
        self.assertEqual(resolve(url).func.cls, UserViewSet)

        url = reverse('user-detail', args=[1])
        self.assertEqual(resolve(url).func.cls, UserViewSet)

    def test_parking_lots_urls(self):
        """Test parking lots app URLs"""
        # Parking Lot List/Create
        url = reverse('parking-lot-list')
        self.assertEqual(resolve(url).func.cls, ParkingLotViewSet)

        # Parking Lot Detail
        url = reverse('parking-lot-detail', args=[1])
        self.assertEqual(resolve(url).func.cls, ParkingLotViewSet)

        # Parking Space List/Create
        url = reverse('parking-space-list')
        self.assertEqual(resolve(url).func.cls, ParkingSpaceViewSet)

        # Parking Space Detail
        url = reverse('parking-space-detail', args=[1])
        self.assertEqual(resolve(url).func.cls, ParkingSpaceViewSet)

        # Parking Space Reserve
        url = reverse('parking-space-reserve', args=[1])
        self.assertEqual(resolve(url).func.cls, ParkingSpaceViewSet)

        # Parking Space Occupy
        url = reverse('parking-space-occupy', args=[1])
        self.assertEqual(resolve(url).func.cls, ParkingSpaceViewSet)

        # Parking Space Vacate
        url = reverse('parking-space-vacate', args=[1])
        self.assertEqual(resolve(url).func.cls, ParkingSpaceViewSet)

    def test_reservations_urls(self):
        """Test reservations app URLs"""
        # Reservation List/Create
        url = reverse('reservation-list')
        self.assertEqual(resolve(url).func.cls, ReservationViewSet)

        # Reservation Detail
        url = reverse('reservation-detail', args=[1])
        self.assertEqual(resolve(url).func.cls, ReservationViewSet)

        # My Reservations
        url = reverse('reservation-my-reservations')
        self.assertEqual(resolve(url).func.cls, ReservationViewSet)

        # Active Reservations
        url = reverse('reservation-active')
        self.assertEqual(resolve(url).func.cls, ReservationViewSet)

        # Cancel Reservation
        url = reverse('reservation-cancel', args=[1])
        self.assertEqual(resolve(url).func.cls, ReservationViewSet)

    def test_url_names(self):
        """Test URL name patterns"""
        # Test URL name patterns for accounts
        self.assertEqual(reverse('user-register'), '/api/auth/register/')
        self.assertEqual(reverse('user-login'), '/api/auth/login/')
        self.assertEqual(reverse('user-profile'), '/api/auth/profile/')
        self.assertEqual(reverse('user-change-password'), '/api/auth/change-password/')
        self.assertEqual(reverse('user-list'), '/api/auth/users/')
        self.assertEqual(reverse('user-detail', args=[1]), '/api/auth/users/1/')

        # Test URL name patterns for parking lots
        self.assertEqual(reverse('parking-lot-list'), '/api/user/parking-lots/')
        self.assertEqual(reverse('parking-lot-detail', args=[1]), '/api/user/parking-lots/1/')
        self.assertEqual(reverse('parking-space-list'), '/api/user/spaces/')
        self.assertEqual(reverse('parking-space-detail', args=[1]), '/api/user/spaces/1/')
        self.assertEqual(reverse('parking-space-reserve', args=[1]), '/api/user/spaces/1/reserve/')
        self.assertEqual(reverse('parking-space-occupy', args=[1]), '/api/user/spaces/1/occupy/')
        self.assertEqual(reverse('parking-space-vacate', args=[1]), '/api/user/spaces/1/vacate/')

        # Test URL name patterns for reservations
        self.assertEqual(reverse('reservation-list'), '/api/user/reservations/')
        self.assertEqual(reverse('reservation-detail', args=[1]), '/api/user/reservations/1/')
        self.assertEqual(reverse('reservation-my-reservations'), '/api/user/reservations/my/')
        self.assertEqual(reverse('reservation-active'), '/api/user/reservations/active/')
        self.assertEqual(reverse('reservation-cancel', args=[1]), '/api/user/reservations/1/cancel/') 