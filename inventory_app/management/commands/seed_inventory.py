from django.core.management.base import BaseCommand
from inventory_app.models import UniformCatalog, Inventory
from django.db import transaction
from django.db import connection


class Command(BaseCommand):
    help = 'Seeds inventory data into the database'

    def handle(self, *args, **kwargs):
        inventory_data = [
            ("S Grey Marbled Short Sleeve", 23, 0, 15, 38, 0, 0),
            ("M Grey Marbled Short Sleeve", 48, 0, 140, 188, 0, 0),
            ("L Grey Marbled Short Sleeve", 41, 10, 78, 129, 0, 0),
            ("XL Grey Marbled Short Sleeve", 41, 6, 34, 81, 0, 0),
            ("2XL Grey Marbled Short Sleeve", 31, 0, 0, 31, 0, 0),
            ("3XL Grey Marbled Short Sleeve", 15, 0, 21, 36, 0, 0),
            ("S Purple Short Sleeve", 1, 0, 1, 2, 0, 0),
            ("M Purple Short Sleeve", 9, 0, 0, 9, 0, 0),
            ("L Purple Short Sleeve", 6, 0, 0, 6, 0, 0),
            ("XL Purple Short Sleeve", 9, 0, 0, 9, 0, 0),
            ("2XL Purple Short Sleeve", 0, 0, 0, 0, 0, 0),
            ("S Black Short Sleeve", 10, 3, 3, 13, 0, 0),
            ("M Black Short Sleeve", 15, 3, 3, 18, 0, 0),
            ("L Black Short Sleeve", 14, 3, 3, 17, 0, 0),
            ("XL Black Short Sleeve", 1, 0, 0, 1, 0, 0),
            ("2XL Black Short Sleeve", 1, 5, 0, 6, 0, 0),
            ("3XL Black Short Sleeve", 0, 0, 0, 0, 0, 0),
            ("XL Short Sleeve Misc.", 0, 2, 0, 2, 0, 0),
            ("S Charcoal Long Sleeve", 20, 1, 0, 21, 0, 0),
            ("M Charcoal Long Sleeve", 50, 18, 0, 68, 0, 0),
            ("L Charcoal Long Sleeve", 31, 11, 0, 42, 0, 0),
            ("XL Charcoal Long Sleeve", 74, 8, 0, 82, 0, 0),
            ("2XL Charcoal Long Sleeve", 40, 8, 0, 48, 0, 0),
            ("3XL Charcoal Long Sleeve", 20, 2, 0, 22, 0, 0),
            ("S Charcoal Breast Cancer", 7, 1, 0, 8, 0, 0),
            ("M Charcoal Breast Cancer", 54, 7, 0, 61, 0, 0),
            ("L Charcoal Breast Cancer", 24, 2, 0, 26, 0, 0),
            ("XL Charcoal Breast Cancer", 34, 1, 0, 35, 0, 0),
            ("3XL Charcoal Breast Cancer", 4, 0, 0, 4, 0, 0),
            ("XS Light Grey Breast Cancer", 5, 1, 0, 6, 0, 0),
            ("S Light Grey Breast Cancer", 5, 2, 0, 7, 0, 0),
            ("M Light Grey Breast Cancer", 10, 5, 0, 15, 0, 0),
            ("L Light Grey Breast Cancer", 4, 4, 0, 8, 0, 0),
            ("XL Light Grey Breast Cancer", 6, 1, 0, 7, 0, 0),
            ("2XL Light Grey Breast Cancer", 2, 3, 0, 5, 0, 0),
            ("S Grey Sweater", 2, 1, 0, 3, 0, 0),
            ("M Grey Sweater", 0, 7, 0, 7, 0, 0),
            ("L Grey Sweater", 3, 6, 0, 9, 0, 0),
            ("XL Grey Sweater", 2, 5, 0, 7, 0, 0),
            ("2XL Grey Sweater", 8, 2, 0, 10, 0, 0),
            ("3XL Grey Sweater", 2, 2, 0, 4, 0, 0),
            ("S Black Shorts", 30, 16, 0, 46, 0, 0),
            ("M Black Shorts", 20, 59, 0, 79, 0, 0),
            ("L Black Shorts", 51, 16, 0, 67, 0, 0),
            ("XL Black Shorts", 30, 4, 12, 46, 0, 0),
            ("2XL Black Shorts", 24, 9, 0, 44, 0, 0),
            ("3XL Black Shorts", 15, 0, 0, 15, 0, 0),
            ("S Sweatpants", 0, 0, 0, 0, 0, 0),
            ("M Sweatpants", 0, 5, 0, 5, 0, 0),
            ("L Sweatpants", 9, 5, 0, 14, 0, 0),
            ("XL Sweatpants", 11, 0, 0, 11, 0, 0),
            ("2XL Sweatpants", 0, 2, 0, 2, 0, 0),
            ("S Hoodie", 20, 0, 0, 20, 0, 0),
            ("M Hoodie", 29, 1, 17, 47, 0, 0),
            ("L Hoodie", 38, 2, 9, 49, 0, 0),
            ("XL Hoodie", 34, 1, 6, 41, 0, 0),
            ("XXL Hoodie", 15, 0, 3, 18, 0, 0),
            ("XXXL Hoodie", 8, 0, 4, 12, 0, 0),
            ("S MGMT Hoodie", 1, 0, 0, 1, 0, 0),
            ("M MGMT Hoodie", 3, 0, 0, 3, 0, 0),
            ("L MGMT Hoodie", 2, 0, 0, 2, 0, 0),
            ("XL MGMT Hoodie", 2, 0, 0, 2, 0, 0),
            ("2XL MGMT Hoodie", 1, 0, 0, 1, 0, 0),
            ("3XL MGMT Hoodie", 0, 0, 0, 0, 0, 0),
            ("Cooling Gaiters", 39, 0, 1, 40, 0, 0),
            ("Grey Cooling Gaiters", 26, 0, 0, 26, 0, 0),
            ("Rain Ponchos", 56, 2, 8, 66, 0, 0),
            ("Rain Suits", 0, 5, 0, 5, 0, 0),
            ("S Rain Pants", 0, 1, 0, 1, 0, 0),
            ("M Rain Pants", 0, 7, 0, 7, 0, 0),
            ("L Rain Pants", 8, 2, 0, 10, 0, 0),
            ("XL Rain Pants", 5, 1, 0, 6, 0, 0),
            ("2XL Rain Pants", 2, 1, 0, 3, 0, 0),
            ("3XL Rain Pants", 6, 0, 0, 6, 0, 0),
            ("S Rain Jackets", 0, 1, 0, 1, 0, 0),
            ("M Rain Jackets", 0, 5, 0, 5, 0, 0),
            ("L Rain Jackets", 2, 12, 0, 14, 0, 0),
            ("XL Rain Jackets", 5, 3, 0, 8, 0, 0),
            ("2XL Rain Jackets", 1, 0, 0, 1, 0, 0),
            ("3XL Rain Jackets", 4, 1, 0, 5, 0, 0),
            ("Golf Camping Coat", 0, 0, 0, 0, 0, 0),
            ("Heated Jacket", 0, 0, 0, 0, 0, 0),
            ("Beanie", 51, 13, 0, 64, 0, 0),
            ("Hat (B)", 33, 1, 2, 36, 0, 0),
            ("Hat (WB)", 2, 3, 47, 52, 0, 0),
            ("Cooling Hats", 3, 0, 0, 3, 0, 0),
            ("Belts", 22, 0, 0, 22, 0, 0),
            ("Orange Safety Vests", 14, 1, 0, 15, 0, 0),
            ("Pink Safety Vests", 5, 0, 0, 5, 0, 0),
            ("S Pants", 4, 0, 0, 4, 0, 0),
            ("M Pants", 2, 0, 0, 2, 0, 0),
            ("L Pants", 4, 0, 0, 4, 0, 0),
            ("XL Pants", 4, 0, 0, 4, 0, 0),
            ("2XL Pants", 2, 0, 0, 2, 0, 0),
            ("3XL Pants", 1, 0, 0, 1, 0, 0),
            ("XS Polos-Male", 0, 0, 0, 0, 0, 0),
            ("S Polos-Male", 0, 0, 0, 0, 0, 0),
            ("M Polos-Male", 3, 5, 0, 8, 0, 0),
            ("L Polos-Male", 12, 12, 0, 24, 0, 0),
            ("XL Polos-Male", 18, 4, 0, 22, 0, 0),
            ("2XL Polos-Male", 5, 0, 0, 5, 0, 0),
            ("3XL Polos-Male", 5, 5, 0, 10, 0, 0),
            ("XS Polos-Female", 0, 5, 0, 5, 0, 0),
            ("S Polos-Female", 0, 0, 0, 0, 0, 0),
            ("M Polos-Female", 6, 0, 0, 6, 0, 0),
            ("L Polos-Female", 8, 4, 0, 12, 0, 0),
            ("XL Polos-Female", 5, 4, 0, 9, 0, 0),
            ("2XL Polos-Female", 3, 9, 0, 12, 0, 0),
            ("3XL Polos-Female", 0, 0, 0, 0, 0, 0),
            ("S Jacket-Male", 0, 0, 0, 0, 0, 0),
            ("M Jacket-Male", 2, 0, 0, 2, 0, 0),
            ("L Jacket-Male", 2, 0, 0, 2, 0, 0),
            ("XL Jacket-Male", 1, 0, 0, 1, 0, 0),
            ("2XL Jacket-Male", 0, 0, 0, 0, 0, 0),
            ("3XL Jacket-Male", 0, 0, 0, 0, 0, 0),
            ("S Jacket-Female", 0, 0, 0, 0, 0, 0),
            ("M Jacket-Female", 1, 0, 0, 1, 0, 0),
            ("L Jacket-Female", 1, 0, 0, 1, 0, 0),
            ("XL Jacket-Female", 1, 0, 0, 1, 0, 0),
            ("2XL Jacket-Female", 1, 0, 0, 1, 0, 0),
            ("3XL Jacket-Female", 0, 0, 0, 0, 0, 0),
            ("39 shoes", 1, 0, 0, 1, 0, 0),
            ("40 shoes", 2, 0, 0, 2, 0, 0),
            ("41 shoes", 1, 0, 0, 1, 0, 0),
            ("42 shoes", 1, 0, 0, 1, 0, 0),
            ("43 shoes", 1, 0, 0, 1, 0, 0),
            ("44 shoes", 0, 0, 0, 0, 0, 0),
            ("45 shoes", 1, 0, 0, 1, 0, 0),
            ("46 shoes", 3, 0, 0, 3, 0, 0),
            ("47 shoes", 1, 0, 0, 1, 0, 0),
            ("48 shoes", 1, 0, 0, 1, 0, 0),
            ("Golf Polo Jackets - Light Blue", 0, 0, 0, 0, 0, 0),
            ("S Golf Polo Jackets - Light Blue", 0, 0, 1, 1, 0, 0),
            ("XL Golf Polo Jackets - Light Blue", 0, 0, 2, 2, 2, 0),
            ("S Golf Polo Jackets - Dark Blue", 0, 0, 1, 1, 0, 0),
            ("XL Golf Polo Jackets - Dark Blue", 0, 0, 2, 2, 0, 0),
            ("S Golf Polo Jackets - Grey", 0, 0, 1, 1, 0, 0),
            ("XLGolf Polo Jackets - Grey", 0, 0, 2, 2, 0, 0),
            ("S Golf Polo Jackets - Black", 0, 0, 1, 1, 0, 0),
            ("XL Golf Polo Jackets - Black", 0, 0, 2, 2, 0, 0)
        ]

        try:
            # Reset the sequence to avoid conflicts with existing ids
            self.reset_inventory_sequence()

            # Iterate through each inventory entry and add it
            with transaction.atomic():
                uniforms_to_create = []
                for uniform in inventory_data:
                    uniform_instance = UniformCatalog.objects.filter(name=uniform[0]).first()

                    # Only proceed if the uniform exists
                    if uniform_instance:
                        # Check if the inventory for the given uniform already exists
                        existing_inventory = Inventory.objects.filter(uniform=uniform_instance).first()
                        if not existing_inventory:  # If no existing inventory, create a new one
                            inventory_instance = Inventory(
                                uniform=uniform_instance,
                                new_stock=uniform[1],
                                used_stock=uniform[2],
                                in_use=uniform[3],
                                disposed=uniform[4],
                                return_to_supplier=uniform[5],
                                total_bought=uniform[6]
                            )
                            uniforms_to_create.append(inventory_instance)

                # Bulk insert into the Inventory table
                if uniforms_to_create:
                    Inventory.objects.bulk_create(uniforms_to_create)
                    self.stdout.write(self.style.SUCCESS("✅ Inventory data seeded successfully!"))
                else:
                    self.stdout.write(self.style.SUCCESS("✅ No new inventory records to seed."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ An error occurred: {e}"))

    def reset_inventory_sequence(self):
        """
        Resets the sequence for the inventory_app_inventory table
        to ensure the id is properly incremented.
        """
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT setval(pg_get_serial_sequence('inventory_app_inventory', 'id'), 
                              COALESCE((SELECT MAX(id) FROM inventory_app_inventory), 1), false);
            """)
            self.stdout.write(self.style.SUCCESS("✅ Inventory sequence reset successfully!"))
