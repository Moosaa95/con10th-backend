from django.core.management.base import BaseCommand
from general.models import Country, State

class Command(BaseCommand):
    help = "Populate the Country and State models with initial data."

    def handle(self, *args, **kwargs):
        country_data = [
            {"name": "Nigeria", "code": "NG"},
            {"name": "United States", "code": "US"},
            {"name": "United Kingdom", "code": "UK"},
        ]

        state_data = {
            "NG": [
                {"name": "Lagos", "code": "LA"},
                {"name": "Abuja", "code": "ABJ"},
            ],
            "US": [
                {"name": "California", "code": "CA"},
                {"name": "Texas", "code": "TX"},
            ],
            "UK": [
                {"name": "London", "code": "LDN"},
                {"name": "Manchester", "code": "MAN"},
            ],
        }

        # Insert countries
        for data in country_data:
            country, created = Country.objects.get_or_create(name=data["name"], code=data["code"])
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created country: {country.name}"))

        # Insert states
        for country_code, states in state_data.items():
            country = Country.objects.get(code=country_code)
            for state in states:
                state_obj, created = State.objects.get_or_create(name=state["name"], code=state["code"], country=country)
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Added state: {state_obj.name} in {country.name}"))

        self.stdout.write(self.style.SUCCESS("Country and State data populated successfully!"))
