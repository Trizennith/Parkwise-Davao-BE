from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.parking_lots.models import ParkingLot, ParkingSpace
from apps.reservations.models import Reservation
from django.utils import timezone
from datetime import timedelta
import random
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')

        # Create admin user
        admin = User.objects.create_user(
            email='admin@example.com',
            username='admin',
            password='admin123',
            first_name='Admin',
            last_name='User',
            role='admin',
            is_staff=True,
            is_superuser=True
        )
        self.stdout.write(self.style.SUCCESS('Created admin user'))

        # Create regular users
        users = []
        for i in range(5):
            user = User.objects.create_user(
                email=f'user{i}@example.com',
                username=f'user{i}',
                password='user123',
                first_name=f'User{i}',
                last_name='Test',
                role='user',
                is_staff=False,
                is_superuser=False
            )
            users.append(user)
        self.stdout.write(self.style.SUCCESS('Created regular users'))

        # Create parking lots
        parking_lots = []
        locations = [
            {'name': 'SM City Davao', 'lat': 7.0731, 'lng': 125.6128, 'address': 'Quimpo Blvd, Davao City'},
            {'name': 'Abreeza Mall', 'lat': 7.0682, 'lng': 125.6087, 'address': 'J.P. Laurel Ave, Davao City'},
            {'name': 'Gaisano Mall', 'lat': 7.0725, 'lng': 125.6135, 'address': 'J.P. Laurel Ave, Davao City'},
            {'name': 'NCCC Mall', 'lat': 7.0715, 'lng': 125.6145, 'address': 'J.P. Laurel Ave, Davao City'},
            {'name': 'Victoria Plaza', 'lat': 7.0705, 'lng': 125.6155, 'address': 'J.P. Laurel Ave, Davao City'},
        ]

        for loc in locations:
            total_spaces = random.randint(50, 200)
            available_spaces = random.randint(10, total_spaces)  # Ensure available_spaces <= total_spaces
            lot = ParkingLot.objects.create(
                name=loc['name'],
                latitude=Decimal(str(loc['lat'])),
                longitude=Decimal(str(loc['lng'])),
                address=loc['address'],
                total_spaces=total_spaces,
                available_spaces=available_spaces,
                status='active',
                hourly_rate=Decimal('50.00')  # Default hourly rate of 50 pesos
            )
            parking_lots.append(lot)
        self.stdout.write(self.style.SUCCESS('Created parking lots'))

        # Create parking spaces for each lot
        for lot in parking_lots:
            # Get a short prefix from the lot name (first 3 letters)
            prefix = lot.name[:3].upper()
            for i in range(lot.total_spaces):
                # Calculate how many spaces should be available
                should_be_available = i < lot.available_spaces
                ParkingSpace.objects.create(
                    parking_lot=lot,
                    space_number=f"{prefix}{i+1:03d}",  # Format: "SMC001", "ABR001", etc.
                    status='available' if should_be_available else 'occupied'
                )
        self.stdout.write(self.style.SUCCESS('Created parking spaces'))

        # Create some reservations
        total_reservations = 0
        for user in users:
            reservations_per_user = 0
            while reservations_per_user < 3:  # Try to create up to 3 reservations per user
                lot = random.choice(parking_lots)
                # Get an available parking space from the lot
                available_spaces = ParkingSpace.objects.filter(
                    parking_lot=lot,
                    status='available'
                )
                
                if not available_spaces.exists():
                    self.stdout.write(self.style.WARNING(f'No available spaces in {lot.name}, skipping...'))
                    break
                
                space = random.choice(list(available_spaces))
                start_time = timezone.now() + timedelta(days=random.randint(1, 7))
                end_time = start_time + timedelta(hours=random.randint(1, 4))
                
                try:
                    Reservation.objects.create(
                        parking_lot=lot,
                        parking_space=space,
                        user=user,
                        vehicle_plate=f"ABC{random.randint(100, 999)}",
                        start_time=start_time,
                        end_time=end_time,
                        status='active',
                        notes=f"Reservation for {user.get_full_name()}"
                    )
                    reservations_per_user += 1
                    total_reservations += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error creating reservation: {str(e)}'))
                    break

        self.stdout.write(self.style.SUCCESS(f'Created {total_reservations} reservations'))
        self.stdout.write(self.style.SUCCESS('Successfully seeded data')) 