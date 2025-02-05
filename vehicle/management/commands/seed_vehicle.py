from django.core.management.base import BaseCommand
from django.db import transaction
from vehicle.models import Vehicle

class Command(BaseCommand):
    help = 'Seeds vehicle (truck and trailer) information into the database'

    def handle(self, *args, **kwargs):
        # Truck and trailer data without duplicates
        vehicle_data = [
            # Truck data (from previous message)
            'Truck 1', 'Truck 2', 'Truck 3', 'Truck 4', 'Truck 5', 'Truck 6', 'Truck 7', 
            'Truck 9', 'Truck 10', 'Truck 11', 'Truck 12', 'Truck 13', 'A&H 1', 'A&H 2', 
            'A&H 3', 'A&H 4', 'QD 1', 'QD 2', 'QD 3', 'QD 4', 'RW 1', 'RW 2', 'RW 3', 
            'Box Truck', 'new truck', 'abc', 'halllo', '16ft Cargo',
            
            # Trailer data (from your message)
            'Trailer 1', 'Trailer 2', 'Trailer 3', 'Trailer 4', 'Trailer 5', 'Trailer 6', 
            'Trailer 7', 'Trailer 8', 'Trailer 9', 'Trailer 10', 'Trailer 11', 'Trailer 12', 
            'Trailer 13', 'Trailer 14', 'Trailer 15', 'Trailer 16', 'Trailer 17', 'Trailer 18',
            'Trailer 19', 'Trailer 20', 'Trailer 21', 'Trailer 22', '16ft Cargo', 'fsdfsdf'
        ]
        
        # Create unique vehicle entries (trucks and trailers)
        vehicles = []
        for number in vehicle_data:
            vehicles.append(
                {'vehicle_type': 'truck' if 'Truck' in number else 'trailer', 'number': number}
            )
        
        # Remove duplicates by converting the list of dictionaries to a set of tuples (number, type)
        unique_vehicles = set(
            (vehicle['number'], vehicle['vehicle_type']) for vehicle in vehicles
        )
        
        # Convert back to a list of dictionaries
        vehicles_to_create = [{'vehicle_type': vehicle_type, 'number': number} for number, vehicle_type in unique_vehicles]

        # Start database transaction
        try:
            with transaction.atomic():
                # Prepare Vehicle objects for creation
                vehicles_to_create_objects = [
                    Vehicle(vehicle_type=vehicle['vehicle_type'], number=vehicle['number'])
                    for vehicle in vehicles_to_create
                ]
                
                # Bulk create Vehicles
                Vehicle.objects.bulk_create(vehicles_to_create_objects)
                
            self.stdout.write(self.style.SUCCESS('Vehicles seeded successfully!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {e}"))
