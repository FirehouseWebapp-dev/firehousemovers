from django.core.management.base import BaseCommand
from django.db import transaction
from inventory_app.models import InventoryTransaction, UniformCatalog
from datetime import datetime


class Command(BaseCommand):
    help = "Seeds inventory transaction data into the database"

    def handle(self, *args, **kwargs):
        # Data format: (Date, Transaction Type, Uniform Name, Quantity, Condition, Notes)
        transactions_data = [
            (
                "10/16/2024 22:42:35",
                "Purchase",
                "S Golf Polo Jackets - Light Blue",
                1,
                "New",
                "",
            ),
            (
                "10/16/2024 22:42:50",
                "Purchase",
                "XL Golf Polo Jackets - Light Blue",
                2,
                "New",
                "",
            ),
            (
                "10/16/2024 22:43:04",
                "Purchase",
                "S Golf Polo Jackets - Dark Blue",
                1,
                "New",
                "",
            ),
            (
                "10/16/2024 22:43:25",
                "Purchase",
                "XL Golf Polo Jackets - Light Blue",
                2,
                "New",
                "",
            ),
            (
                "10/16/2024 22:43:54",
                "Dispose",
                "XL Golf Polo Jackets - Light Blue",
                2,
                "New",
                "added by accident",
            ),
            (
                "10/16/2024 22:44:20",
                "Purchase",
                "XL Golf Polo Jackets - Dark Blue",
                2,
                "New",
                "",
            ),
            (
                "10/16/2024 22:44:36",
                "Purchase",
                "S Golf Polo Jackets - Grey",
                1,
                "New",
                "",
            ),
            (
                "10/16/2024 22:44:54",
                "Purchase",
                "XLGolf Polo Jackets - Grey",
                2,
                "New",
                "",
            ),
            (
                "10/16/2024 22:45:09",
                "Purchase",
                "S Golf Polo Jackets - Black",
                1,
                "New",
                "",
            ),
            (
                "10/16/2024 22:45:23",
                "Purchase",
                "XL Golf Polo Jackets - Black",
                2,
                "New",
                "",
            ),
            ("11/4/2024 23:17:23", "Purchase", "S Hoodie", 20, "New", ""),
            (
                "11/4/2024 23:17:41",
                "Purchase",
                "S Grey Marbled Short Sleeve",
                20,
                "New",
                "",
            ),
            (
                "11/4/2024 23:18:01",
                "Purchase",
                "M Grey Marbled Short Sleeve",
                75,
                "New",
                "",
            ),
            (
                "11/4/2024 23:18:52",
                "Purchase",
                "3XL Grey Marbled Short Sleeve",
                8,
                "New",
                "",
            ),
            ("11/4/2024 23:19:06", "Purchase", "XL Hoodie", 10, "New", ""),
            ("11/4/2024 23:19:23", "Purchase", "XXL Hoodie", 7, "New", ""),
            ("11/4/2024 23:19:33", "Purchase", "XXXL Hoodie", 5, "New", ""),
            ("11/4/2024 23:19:45", "Purchase", "M Hoodie", 5, "New", ""),
            ("11/4/2024 23:19:59", "Purchase", "L Hoodie", 20, "New", ""),
            ("11/4/2024 23:20:09", "Purchase", "L Hoodie", 15, "New", ""),
            ("11/4/2024 23:20:25", "Purchase", "XL Hoodie", 10, "New", ""),
            ("11/4/2024 23:20:43", "Purchase", "S Charcoal Long Sleeve", 8, "New", ""),
            ("11/4/2024 23:20:59", "Purchase", "M Charcoal Long Sleeve", 50, "New", ""),
            (
                "11/20/2024 17:49:05",
                "Purchase",
                "S Grey Marbled Short Sleeve",
                222,
                "New",
                "",
            ),
            (
                "11/20/2024 17:50:18",
                "Purchase",
                "S Grey Marbled Short Sleeve",
                222,
                "New",
                "",
            ),
        ]

        try:
            with transaction.atomic():
                # Prepare transaction objects for creation
                transactions_to_create = []
                for row in transactions_data:
                    (
                        date_str,
                        transaction_type,
                        uniform_name,
                        quantity,
                        condition,
                        notes,
                    ) = row
                    # Convert date from string to datetime
                    date = datetime.strptime(date_str, "%m/%d/%Y %H:%M:%S")

                    try:
                        # Look up the uniform from UniformCatalog
                        uniform = UniformCatalog.objects.get(name=uniform_name)
                    except UniformCatalog.DoesNotExist:
                        print(f"Uniform '{uniform_name}' not found in catalog.")
                        continue

                    # Create the transaction object
                    transactions = InventoryTransaction(
                        date=date,
                        transaction_type=transaction_type,
                        uniform=uniform,
                        quantity=quantity,
                        condition=condition,
                        notes=notes,
                    )
                    transactions_to_create.append(transactions)

                # Bulk create the transactions
                InventoryTransaction.objects.bulk_create(transactions_to_create)

            self.stdout.write(
                self.style.SUCCESS("Inventory transactions seeded successfully")
            )
            print("✅ Inventory transactions seeded successfully!")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ An error occurred: {e}"))
            print(f"❌ An error occurred: {e}")
