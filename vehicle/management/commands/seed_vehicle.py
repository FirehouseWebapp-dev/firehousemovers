import pandas as pd
from datetime import datetime
from django.db import transaction
from vehicle.models import Vehicle, AvailabilityData  # Adjust to your actual app name

# Load the data from the CSV file or wherever you have it stored
data = [
    ("11/8/2024 5:00:00", "truck", "Truck 1", "Out of Service", "11/30/2024", "12/6/2024", "11/8/2024 19:24:40"),
    ("11/8/2024 5:00:00", "truck", "Truck 2", "In Service", None, None, "11/8/2024 19:24:40"),
    ("11/8/2024 5:00:00", "truck", "Truck 3", "In Service", None, None, "11/8/2024 19:24:40"),
    ("11/8/2024 5:00:00", "truck", "Truck 4", "In Service", None, None, "11/8/2024 19:24:40"),
    ("11/8/2024 5:00:00", "truck", "Truck 5", "In Service", None, None, "11/8/2024 19:24:40"),
    ("11/8/2024 5:00:00", "truck", "Truck 6", "In Service", None, None, "11/8/2024 19:24:40"),
    ("11/8/2024 5:00:00", "truck", "Truck 7", "In Service", None, None, "11/8/2024 19:24:40"),
    ("11/8/2024 5:00:00", "truck", "Truck 9", "In Service", None, None, "11/8/2024 19:24:40"),
    ("11/8/2024 5:00:00", "truck", "Truck 10", "In Service", None, None, "11/8/2024 19:24:40"),
    ("11/8/2024 5:00:00", "truck", "Truck 11", "In Service", None, None, "11/8/2024 19:24:40"),
    ("11/8/2024 5:00:00", "truck", "Truck 12", "In Service", None, None, "11/8/2024 19:24:40"),
    ("11/8/2024 5:00:00", "truck", "Truck 13", "In Service", None, None, "11/8/2024 19:24:40"),
    ("11/8/2024 5:00:00", "truck", "A&H 1", "In Service", None, None, "11/8/2024 19:24:40"),
    ("11/8/2024 5:00:00", "truck", "A&H 2", "In Service", None, None, "11/8/2024 19:24:40"),
    ("11/8/2024 5:00:00", "truck", "A&H 3", "In Service", None, None, "11/8/2024 19:24:40"),
    ("11/8/2024 5:00:00", "truck", "A&H 4", "In Service", None, None, "11/8/2024 19:24:40"),
    ("11/8/2024 5:00:00", "truck", "QD 1", "In Service", None, None, "11/8/2024 19:24:40"),
    ("11/8/2024 5:00:00", "truck", "QD 2", "In Service", None, None, "11/8/2024 19:24:40"),
    ("11/8/2024 5:00:00", "truck", "QD 3", "In Service", None, None, "11/8/2024 19:24:40"),
    ("11/8/2024 5:00:00", "truck", "QD 4", "In Service", None, None, "11/8/2024 19:24:40"),
    ("11/8/2024 5:00:00", "truck", "RW 1", "In Service", None, None, "11/8/2024 19:24:40"),
    ("11/8/2024 5:00:00", "truck", "RW 2", "In Service", None, None, "11/8/2024 19:24:40"),
    ("11/8/2024 5:00:00", "truck", "RW 3", "In Service", None, None, "11/8/2024 19:24:40"),
    ("11/8/2024 5:00:00", "truck", "Box Truck", "In Service", None, None, "11/8/2024 19:24:40"),
    ("11/8/2024 5:00:00", "trailer", "Trailer 1", "In Service", None, None, "11/8/2024 19:24:40"),
    ("11/8/2024 5:00:00", "trailer", "Trailer 2", "In Service", None, None, "11/8/2024 19:24:40"),
    ("11/8/2024 5:00:00", "trailer", "Trailer 3", "In Service", None, None, "11/8/2024 19:24:40"),
    ("11/8/2024 5:00:00", "trailer", "Trailer 4", "In Service", None, None, "11/8/2024 19:24:40"),
    ("11/8/2024 5:00:00", "trailer", "Trailer 5", "In Service", None, None, "11/8/2024 19:24:40"),
    ("11/8/2024 5:00:00", "trailer", "Trailer 6", "In Service", None, None, "11/8/2024 19:24:40"),
    ("11/8/2024 5:00:00", "trailer", "Trailer 7", "In Service", None, None, "11/8/2024 19:24:40"),
    ("11/8/2024 5:00:00", "trailer", "Trailer 8", "In Service", None, None, "11/8/2024 19:24:40"),
    ("11/8/2024 5:00:00", "trailer", "Trailer 9", "In Service", None, None, "11/8/2024 19:24:40"),
    ("11/8/2024 5:00:00", "trailer", "Trailer 10", "In Service", None, None, "11/8/2024 19:24:40"),
    ("11/8/2024 5:00:00", "trailer", "Trailer 11", "In Service", None, None, "11/8/2024 19:24:40"),
    ("11/8/2024 5:00:00", "trailer", "Trailer 12", "In Service", None, None, "11/8/2024 19:24:40"),
    ("11/8/2024 5:00:00", "trailer", "Trailer 13", "In Service", None, None, "11/8/2024 19:24:40"),
    ("11/8/2024 5:00:00", "trailer", "Trailer 14", "In Service", None, None, "11/8/2024 19:24:40"),
    ("11/8/2024 5:00:00", "trailer", "Trailer 15", "In Service", None, None, "11/8/2024 19:24:40"),
    ("11/8/2024 5:00:00", "trailer", "Trailer 16", "In Service", None, None, "11/8/2024 19:24:40"),
    ("11/8/2024 5:00:00", "trailer", "Trailer 17", "In Service", None, None, "11/8/2024 19:24:40"),
    ("11/8/2024 5:00:00", "trailer", "Trailer 18", "In Service", None, None, "11/8/2024 19:24:40"),
    ("11/8/2024 5:00:00", "trailer", "Trailer 19", "In Service", None, None, "11/8/2024 19:24:40"),
    ("11/8/2024 5:00:00", "trailer", "Trailer 20", "In Service", None, None, "11/8/2024 19:24:40"),
    ("11/8/2024 5:00:00", "trailer", "Trailer 21", "In Service", None, None, "11/8/2024 19:24:40"),
    ("11/8/2024 5:00:00", "trailer", "Trailer 22", "In Service", None, None, "11/8/2024 19:24:40"),
    ("11/8/2024 5:00:00", "trailer", "Trailer 23", "In Service", None, None, "11/8/2024 19:24:40"),
    ("11/8/2024 5:00:00", "trailer", "Trailer 24", "In Service", None, None, "11/8/2024 19:24:40")
]


# Convert the data into a DataFrame
df = pd.DataFrame(data, columns=["Date", "Vehicle Type", "Vehicle Number", "Status", "Estimated Back In Service Date", "Actual Back In Service Date", "Date Saved"])

# Prepare a list for AvailabilityData instances
availability_to_create = []

# Loop through each row and prepare AvailabilityData instances
for index, row in df.iterrows():
    try:
        # Get the vehicle object (handle cases where the vehicle might not exist)
        vehicle = Vehicle.objects.get(vehicle_number=row["Vehicle Number"])

        estimated_back_in_service_date = datetime.strptime(row["Estimated Back In Service Date"], "%m/%d/%Y") if row["Estimated Back In Service Date"] else None
        back_in_service_date = datetime.strptime(row["Actual Back In Service Date"], "%m/%d/%Y") if row["Actual Back In Service Date"] else None
        date_saved = datetime.strptime(row["Date Saved"], "%m/%d/%Y %H:%M:%S")

        # Create AvailabilityData dictionary
        availability_data = {
            'vehicle': vehicle,
            'status': row["Status"],
            'estimated_back_in_service_date': estimated_back_in_service_date,
            'back_in_service_date': back_in_service_date,
            'date_saved': date_saved,
        }

        # Add to the list of instances to be created
        availability_to_create.append(AvailabilityData(**availability_data))
    
    except Vehicle.DoesNotExist:
        print(f"Vehicle with number {row['Vehicle Number']} does not exist.")
        continue

# Remove duplicates from the list if any, based on the combination of vehicle and status
# Create a set of tuples (vehicle_id, status, start_date, end_date) for uniqueness
unique_availability = set(
    (avail.vehicle.id, avail.status, avail.start_date, avail.end_date) for avail in availability_to_create
)

# Convert the set back to AvailabilityData objects
unique_availability_objects = [
    AvailabilityData(
        vehicle=Vehicle.objects.get(id=vehicle_id),
        status=status,
        start_date=start_date,
        end_date=end_date
    )
    for vehicle_id, status, start_date, end_date in unique_availability
]

# Start database transaction for bulk creation
try:
    with transaction.atomic():
        # Bulk create AvailabilityData instances
        AvailabilityData.objects.bulk_create(unique_availability_objects)
    print("Availability data import complete!")
except Exception as e:
    print(f"An error occurred while importing data: {e}")
