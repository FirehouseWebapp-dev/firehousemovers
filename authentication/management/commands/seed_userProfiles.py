from django.contrib.auth.models import User
from authentication.models import UserProfile
from django.db import transaction
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Seeds user data into the database"

    def handle(self, *args, **kwargs):
        # User data (Username)
        userProfiles = {
            "Adam Rozen": "llc/field",
            "Alaciel Hernandez": "llc/owner",
            "Alex Fichera": "llc/field",
            "Alexandria Blackburn": "sales",
            "Alexzander Strachan": "field",
            "Alfonso Ambriez": "llc/field",
            "Angel Ronaiderson Cantillo": "llc/field",
            "Anton Shashirov": "admin",
            "Ashley Hammond": "sales",
            "Brianna Herrera": "admin",
            "Bryce Nicolai": "field",
            "Cavarsier Williams": "llc/field",
            "Chelsie Willette": "sales",
            "Chris Havanis": "field",
            "Christopher Sales": "llc/owner",
            "Darion Prioleau": "llc/field",
            "David Ramos": "llc/field",
            "David Suazo Antunez": "llc/field",
            "Denis Hernandez": "llc/field",
            "Diego Contreras": "field",
            "Dylan Barber": "llc/field",
            "Dymon Cobb": "sales",
            "Edwin Videla": "field",
            "Elijah Garza": "llc/field",
            "Eric Menchaca": "llc/field",
            "Erick Sanchez": "llc/field",
            "Erix Rosales": "llc/field",
            "Filiberto Santos": "llc/field",
            "Gabriel Guillaron": "llc/field",
            "Gabriel Sanchez": "llc/field",
            "Geovany Rodriguez": "llc/field",
            "Gerardo Zapata": "field",
            "Humberto Munoz": "field",
            "Isreal Ara": "field",
            "Jacobi Wells": "llc/field",
            "Jairo Mendez": "llc/field",
            "James Hutchinson": "field",
            "Javier Garcia": "llc/field",
            "Jay Adams": "llc/owner",
            "Joel Paez": "rwh",
            "John Autrey": "llc/field",
            "John Castillo": "llc/field",
            "John Wanderi": "rwh",
            "Jonathan Stanzak": "field",
            "Jordan Trent": "field",
            "Jorge Hernandez": "llc/field",
            "Jorge Palma": "llc/field",
            "Jose Moreno": "llc/field",
            "Jose Noe Martinez": "llc/field",
            "Joseph Hawkins": "field",
            "Juan Torres": "llc/field",
            "Julian Hernandez": "llc/field",
            "Julio Benitez": "llc/field",
            "Kevin Dunigan": "field",
            "Kwesi Brinson": "field",
            "Leon Kaoma": "admin",
            "Logan Foster": "field",
            "Mark Vega": "field",
            "Michael Flagg": "field",
            "Miguel Flores": "llc/field",
            "Moses Jenkis": "field",
            "Nicole Ingram": "sales",
            "Oscar Miranda": "llc/field",
            "Philip Myers": "field",
            "Rendell Carter": "llc/field",
            "Richard Wright": "field",
            "Robert Jander": "admin",
            "Roiman Veroes": "warehouse",
            "Ronald Miguel Arvelo": "llc/field",
            "Ruben Guillaron": "llc/field",
            "Santiago Rodriguez": "llc/field",
            "Sheynen Seguin": "admin",
            "Stephen Arevalo": "field",
            "Thomas Jewell": "field",
            "Trevor Ashman": "llc/field",
            "Vernon Raber": "llc/field",
            "Vidal C Rojas": "llc/field",
            "Zidane Rodriguez": "llc/field",
            "Julian Hernandez Sr.": "mover",
            "Rogelio Santillana": "mover",
            "Etc": "customers- per trevor",
            "Jose Rebollar": "mover",
            "Peter Taylor": "mover - crew member",
            # Managers
            "Brian": "manager",
            "Robert": "manager",
            "Trevor": "manager",
            "Brianna": "manager",
            "Sheynen": "manager",
            "Jay": "manager",
            "Leon": "manager",
            "Nikki": "manager",
            "David": "manager",
            # Drivers
            "Edwin Videla": "driver",
            "Logan Foster": "driver",
            "Moses Jenkins": "driver",
            "Michael Flagge": "driver",
            "Johnathan Stanzak": "driver",
            "Vernon Raber": "driver",
            "Chris Haranis": "driver",
            "John Castillo": "driver",
            "James Hutchinson": "driver",
            "Jorge Palma": "driver",
            "Vidal Rojas": "driver",
            "John Autrey": "driver",
            "John Wanderi": "driver",
            "Stephen Arevalo": "driver",
            "Richard Wright": "driver",
            "Gerardo Zapata": "driver",
            "Phillip Myers": "driver",
            "Filiberto Santos": "driver",
            "Elijah Garza": "driver",
            "Alex Hernandez": "driver",
            "Jose Moreno": "driver",
            "Jose Noe Martinez": "driver",
            "Jorge Hernandez": "driver",
            "Julian Hernandez": "driver",
        }

        DEFAULT_PASSWORD = "default123"

        try:
            with transaction.atomic():
                # Fetch existing usernames to avoid duplicates
                usernames = list(userProfiles.keys())
                existing_usernames = set(
                    User.objects.filter(username__in=usernames).values_list(
                        "username", flat=True
                    )
                )

                # Prepare User objects for creation
                users_to_create = [
                    User(
                        username=username,
                        email=f"{username.lower().replace(' ', '.')}@default.com",
                    )
                    for username in usernames
                    if username not in existing_usernames
                ]

                # Set password for each user
                for user in users_to_create:
                    user.set_password(DEFAULT_PASSWORD)

                # Bulk create Users
                created_users = User.objects.bulk_create(users_to_create)

                # Prepare UserProfile objects
                profiles_to_create = [
                    UserProfile(user=user, role=userProfiles[user.username])
                    for user in created_users
                ]

                # Bulk create UserProfiles
                UserProfile.objects.bulk_create(profiles_to_create)

            self.stdout.write(self.style.SUCCESS("Data seeded successfully"))

            print("✅ Users and UserProfiles seeded successfully!")

        except Exception as e:
            print(f"❌ An error occurred: {e}")
