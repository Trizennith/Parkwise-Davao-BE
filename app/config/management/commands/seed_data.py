from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from app.api.parking_lots.models import ParkingLot, ParkingSpace
from app.api.reservations.models import Reservation
from app.api.reports.models import DailyReport, MonthlyReport, ParkingLotReport
from django.utils import timezone
from datetime import timedelta, datetime
import random
from decimal import Decimal
from django.db import connection

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with sample data'

    def reset_database(self):
        """Reset the database by dropping all data and resetting sequences."""
        self.stdout.write('Resetting database...')
        
        with connection.cursor() as cursor:
            # Disable foreign key constraints temporarily
            cursor.execute('SET CONSTRAINTS ALL DEFERRED')
            
            # Get all tables in the database
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
            """)
            tables = cursor.fetchall()
            
            # Drop all data from tables
            for table in tables:
                table_name = table[0]
                if table_name != 'django_migrations':  # Skip migrations table
                    self.stdout.write(f'Dropping data from {table_name}...')
                    cursor.execute(f'TRUNCATE TABLE "{table_name}" CASCADE')
            
            # Reset all sequences
            cursor.execute("""
                SELECT sequence_name 
                FROM information_schema.sequences 
                WHERE sequence_schema = 'public'
            """)
            sequences = cursor.fetchall()
            
            for sequence in sequences:
                sequence_name = sequence[0]
                self.stdout.write(f'Resetting sequence {sequence_name}...')
                cursor.execute(f'ALTER SEQUENCE "{sequence_name}" RESTART WITH 1')
            
            # Re-enable foreign key constraints
            cursor.execute('SET CONSTRAINTS ALL IMMEDIATE')
            
        self.stdout.write(self.style.SUCCESS('Database reset complete'))

    def handle(self, *args, **options):
        # Reset the database first
        self.reset_database()
        
        self.stdout.write('Seeding new data...')

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

        # Create regular users with more realistic data
        users = []
        user_data = [
            {'first_name': 'John', 'last_name': 'Doe', 'email': 'john.doe@example.com'},
            {'first_name': 'Jane', 'last_name': 'Smith', 'email': 'jane.smith@example.com'},
            {'first_name': 'Michael', 'last_name': 'Johnson', 'email': 'michael.j@example.com'},
            {'first_name': 'Sarah', 'last_name': 'Williams', 'email': 'sarah.w@example.com'},
            {'first_name': 'David', 'last_name': 'Brown', 'email': 'david.b@example.com'},
        ]

        for user_info in user_data:
            user = User.objects.create_user(
                email=user_info['email'],
                username=user_info['email'].split('@')[0],
                password='user123',
                first_name=user_info['first_name'],
                last_name=user_info['last_name'],
                role='user',
                is_staff=False,
                is_superuser=False
            )
            users.append(user)
        self.stdout.write(self.style.SUCCESS('Created regular users'))

        # Create parking lots with more realistic data
        parking_lots = []
        locations = [
            {
                'name': 'SM City Davao',
                'lat': 7.0731,
                'lng': 125.6128,
                'address': 'Quimpo Blvd, Davao City',
                'total_spaces': 500,
                'hourly_rate': 50.00
            },
            {
                'name': 'Abreeza Mall',
                'lat': 7.0682,
                'lng': 125.6087,
                'address': 'J.P. Laurel Ave, Davao City',
                'total_spaces': 300,
                'hourly_rate': 40.00
            },
            {
                'name': 'Gaisano Mall',
                'lat': 7.0725,
                'lng': 125.6135,
                'address': 'J.P. Laurel Ave, Davao City',
                'total_spaces': 400,
                'hourly_rate': 35.00
            },
            {
                'name': 'NCCC Mall',
                'lat': 7.0715,
                'lng': 125.6145,
                'address': 'J.P. Laurel Ave, Davao City',
                'total_spaces': 350,
                'hourly_rate': 30.00
            },
            {
                'name': 'Victoria Plaza',
                'lat': 7.0705,
                'lng': 125.6155,
                'address': 'J.P. Laurel Ave, Davao City',
                'total_spaces': 250,
                'hourly_rate': 25.00
            },
        ]

        for loc in locations:
            # Calculate available spaces (random between 20% and 80% of total)
            available_spaces = random.randint(
                int(loc['total_spaces'] * 0.2),
                int(loc['total_spaces'] * 0.8)
            )
            
            lot = ParkingLot.objects.create(
                name=loc['name'],
                latitude=Decimal(str(loc['lat'])),
                longitude=Decimal(str(loc['lng'])),
                address=loc['address'],
                total_spaces=loc['total_spaces'],
                available_spaces=available_spaces,
                status=ParkingLot.Status.ACTIVE,
                hourly_rate=Decimal(str(loc['hourly_rate']))
            )
            parking_lots.append(lot)
        self.stdout.write(self.style.SUCCESS('Created parking lots'))

        # Create parking spaces for each lot
        for lot in parking_lots:
            # Get a short prefix from the lot name (first 3 letters)
            prefix = lot.name[:3].upper()
            
            # Calculate how many spaces should be available
            available_count = lot.available_spaces
            total_count = lot.total_spaces
            
            for i in range(total_count):
                # Calculate if space should be available
                should_be_available = i < available_count
                
                ParkingSpace.objects.create(
                    parking_lot=lot,
                    space_number=f"{prefix}{i+1:03d}",  # Format: "SMC001", "ABR001", etc.
                    status=ParkingSpace.Status.AVAILABLE if should_be_available else ParkingSpace.Status.OCCUPIED
                )
        self.stdout.write(self.style.SUCCESS('Created parking spaces'))

        # Create reservations with more realistic data
        total_reservations = 0
        vehicle_plates = [
            'ABC123', 'XYZ789', 'DEF456', 'GHI789', 'JKL012',
            'MNO345', 'PQR678', 'STU901', 'VWX234', 'YZA567'
        ]
        
        # Generate reservations for the last 30 days
        for day in range(30):
            current_date = timezone.now().date() - timedelta(days=day)
            
            for user in users:
                reservations_per_user = random.randint(1, 3)  # Random number of reservations per user
                while reservations_per_user > 0:
                    lot = random.choice(parking_lots)
                    # Get an available parking space from the lot
                    available_spaces = ParkingSpace.objects.filter(
                        parking_lot=lot,
                        status=ParkingSpace.Status.AVAILABLE
                    )
                    
                    if not available_spaces.exists():
                        self.stdout.write(self.style.WARNING(f'No available spaces in {lot.name}, skipping...'))
                        break
                    
                    space = random.choice(list(available_spaces))
                    
                    # Generate realistic reservation times
                    start_time = timezone.make_aware(datetime.combine(
                        current_date,
                        datetime.strptime(f"{random.randint(6, 20)}:{random.choice(['00', '15', '30', '45'])}", "%H:%M").time()
                    ))
                    duration = random.randint(1, 8)  # Random duration between 1 and 8 hours
                    end_time = start_time + timedelta(hours=duration)
                    
                    try:
                        Reservation.objects.create(
                            parking_lot=lot,
                            parking_space=space,
                            user=user,
                            vehicle_plate=random.choice(vehicle_plates),
                            start_time=start_time,
                            end_time=end_time,
                            status='completed',  # Set as completed for historical data
                            notes=f"Reservation for {user.get_full_name()}"
                        )
                        reservations_per_user -= 1
                        total_reservations += 1
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error creating reservation: {str(e)}'))
                        break

        self.stdout.write(self.style.SUCCESS(f'Created {total_reservations} reservations'))

        # Generate reports with more comprehensive data
        self.stdout.write('Generating reports...')
        
        # Generate daily reports for the last 30 days
        for day in range(30):
            current_date = timezone.now().date() - timedelta(days=day)
            
            # Get reservations for the day
            day_reservations = Reservation.objects.filter(
                start_time__date=current_date,
                status='completed'
            )
            
            # Calculate daily statistics
            total_revenue = sum(res.total_cost for res in day_reservations)
            total_reservations = day_reservations.count()
            
            # Calculate average duration
            durations = [res.duration for res in day_reservations]
            average_duration = sum(durations) / len(durations) if durations else 0
            
            # Find peak hour
            hourly_counts = {}
            for res in day_reservations:
                hour = res.start_time.hour
                hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
            
            peak_hour = max(hourly_counts.items(), key=lambda x: x[1])[0] if hourly_counts else None
            if peak_hour is not None:
                peak_hour = datetime.strptime(f"{peak_hour:02d}:00", "%H:%M").time()
            
            # Calculate occupancy rate
            total_spaces = sum(lot.total_spaces for lot in parking_lots)
            occupied_spaces = sum(lot.total_spaces - lot.available_spaces for lot in parking_lots)
            occupancy_rate = (occupied_spaces / total_spaces * 100) if total_spaces > 0 else 0
            
            # Create daily report
            DailyReport.objects.create(
                date=current_date,
                total_revenue=total_revenue,
                total_reservations=total_reservations,
                average_duration=average_duration,
                peak_hour=peak_hour,
                occupancy_rate=occupancy_rate
            )
            
            # Generate parking lot reports for each lot
            for lot in parking_lots:
                lot_reservations = day_reservations.filter(parking_lot=lot)
                lot_revenue = sum(res.total_cost for res in lot_reservations)
                lot_reservations_count = lot_reservations.count()
                lot_durations = [res.duration for res in lot_reservations]
                lot_average_duration = sum(lot_durations) / len(lot_durations) if lot_durations else 0
                
                # Calculate lot-specific peak hour
                lot_hourly_counts = {}
                for res in lot_reservations:
                    hour = res.start_time.hour
                    lot_hourly_counts[hour] = lot_hourly_counts.get(hour, 0) + 1
                
                lot_peak_hour = max(lot_hourly_counts.items(), key=lambda x: x[1])[0] if lot_hourly_counts else None
                if lot_peak_hour is not None:
                    lot_peak_hour = datetime.strptime(f"{lot_peak_hour:02d}:00", "%H:%M").time()
                
                # Calculate lot occupancy rate
                lot_occupancy_rate = ((lot.total_spaces - lot.available_spaces) / lot.total_spaces * 100) if lot.total_spaces > 0 else 0
                
                ParkingLotReport.objects.create(
                    parking_lot=lot,
                    date=current_date,
                    total_revenue=lot_revenue,
                    total_reservations=lot_reservations_count,
                    average_duration=lot_average_duration,
                    peak_hour=lot_peak_hour,
                    occupancy_rate=lot_occupancy_rate
                )
        
        # Generate monthly reports for the last 12 months
        current_date = timezone.now().date()
        for month_offset in range(12):
            target_date = current_date - timedelta(days=30 * month_offset)
            year = target_date.year
            month = target_date.month
            
            # Get reservations for the month
            month_reservations = Reservation.objects.filter(
                start_time__year=year,
                start_time__month=month,
                status='completed'
            )
            
            # Calculate monthly statistics
            total_revenue = sum(res.total_cost for res in month_reservations)
            total_reservations = month_reservations.count()
            
            # Calculate average duration
            durations = [res.duration for res in month_reservations]
            average_duration = sum(durations) / len(durations) if durations else 0
            
            # Calculate average occupancy rate from daily reports
            daily_reports = DailyReport.objects.filter(
                date__year=year,
                date__month=month
            )
            average_occupancy_rate = sum(report.occupancy_rate for report in daily_reports) / len(daily_reports) if daily_reports else 0
            
            # Find peak day
            daily_counts = {}
            for res in month_reservations:
                day = res.start_time.date()
                daily_counts[day] = daily_counts.get(day, 0) + 1
            
            peak_day = max(daily_counts.items(), key=lambda x: x[1])[0] if daily_counts else None
            
            # Create monthly report
            MonthlyReport.objects.create(
                year=year,
                month=month,
                total_revenue=total_revenue,
                total_reservations=total_reservations,
                average_duration=average_duration,
                average_occupancy_rate=average_occupancy_rate,
                peak_day=peak_day
            )
        
        self.stdout.write(self.style.SUCCESS('Successfully generated reports'))
        self.stdout.write(self.style.SUCCESS('Successfully seeded data')) 