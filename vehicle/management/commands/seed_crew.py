from django.core.management.base import BaseCommand
from django.db import transaction
from vehicle.models import Crew


class Command(BaseCommand):
    help = "Seeds crew leaders and members data into the database"

    def handle(self, *args, **kwargs):
        # Crew leaders and members
        leaders = [
            "Mark Vega",
            "Isreal Ara",
            "Joseph Hawkins",
            "Diego Contreras",
            "Carlos Contreras",
            "Thomas Jewell",
            "Oscar Miranda",
            "Julio Benitez",
            "Miguel Flores",
            "Adam Rozen",
            "Jairo Mendez",
            "Juan Torres",
        ]

        members = [
            "Logan Foster",
            "Moses Jenkins",
            "Michael Flagge",
            "Johnathan Stanzak",
            "Vernon Raber",
            "Chris Haranis",
            "John Castillo",
            "Jorge Palma",
            "Vidal Rojas",
            "John Autrey",
            "John Wanderi",
            "Phillip Myers",
            "Filiberto Santos",
            "Elijah Garza",
            "Alex Hernandez",
            "Jose Moreno",
            "Jose Noe Martinez",
            "Jorge Hernandez",
            "Julian Hernandez",
            "Chris Havanis",
            "Daniel West",
            "Darius Lindsey",
            "Darren Fields",
            "Demetrius Jones",
            "Edwin Videla",
            "Gerardo Zapata",
            "Gianfranco Izaguirre",
            "Humberto Munoz",
            "James Hutchinson",
            "Jonathan Stanzak",
            "Kevin Dunigan",
            "Kwesi Brinson",
            "Nathan Dooley",
            "Philip Myers",
            "Richard Wright",
            "Stephen Arevalo",
            "Alaciel Hernandez",
            "Christopher Sales",
            "David Ramos",
            "David Suazo Antunez",
            "Eduardo Flores",
            "Eric Menchaca",
            "Erix Rosales",
            "Geovany Rodriguez",
            "Javier Garcia",
            "Javier Torres",
            "RWH Adam Rozen",
            "RWH Anton Shashirov",
            "RWH Chance Perrin",
            "RWH Jairo Mendez",
            "RWH Jose Rebollar",
            "Ryan Friedman",
            "Santiago Rodriguez",
            "Vidal C Rojas",
            "1-A & H Hauling-Alex",
            "1-QuickDraw- Chris",
            "1-Razor Wire Hauling-Jay",
            "2-A & H Hauling- Alex",
            "2-QuickDraw - Chris",
            "2-Razor Wire Hauling-Jay",
            "3-A & H Hauling- Alex",
            "3-QuickDraw-Chris",
            "4-QuickDraw-Chris",
        ]

        try:
            with transaction.atomic():
                # Prepare Crew objects for creation: Leaders
                crew_to_create = [
                    Crew(name=leader, role="leader") for leader in leaders
                ]

                # Prepare Crew objects for creation: Members
                crew_to_create += [
                    Crew(name=member, role="member") for member in members
                ]

                # Bulk create Crew objects
                Crew.objects.bulk_create(crew_to_create)

            self.stdout.write(
                self.style.SUCCESS("Crew leaders and members seeded successfully")
            )
            print("✅ Crew leaders and members seeded successfully!")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ An error occurred: {e}"))
            print(f"❌ An error occurred: {e}")
