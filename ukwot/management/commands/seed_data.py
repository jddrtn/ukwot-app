# Import Django's base class for custom management commands.
from django.core.management.base import BaseCommand

# Import models.
from ukwot.models import Otter, HealthAssessment, Species

# Faker is used to generate fake names and dates.
from faker import Faker

# Library imports for date handling and randomness.
from datetime import date, timedelta
from decimal import Decimal
import random


class Command(BaseCommand):

    help = "Seed database with realistic otter data and health trends"

    def handle(self, *args, **options):

        fake = Faker()

        self.stdout.write(self.style.WARNING("Starting seed process..."))

        # Get all existing species from the database.

        species_objects = list(Species.objects.all())

        if not species_objects:
            self.stdout.write(
                self.style.ERROR("No species records found. Add species data first.")
            )
            return


        # HealthAssessment.objects.all().delete()
        # Otter.objects.all().delete()

        # A list to store otter objects before bulk creation.
        otters_to_create = []

        # Create 20 otters with realistic names and details.
        for _ in range(20):
            otter = Otter(
                # Use Faker to generate a realistic first name.
                name=fake.first_name(),

                # Pick a random existing species.
                species=random.choice(species_objects),

                # Random gender.
                gender=random.choice(["Male", "Female", "Unknown"]),

                # Give a realistic starting weight.
                weight_kg=Decimal(str(round(random.uniform(4.0, 10.0), 2))),

                # Random status.
                status=random.choice(["Rescued", "Rehabilitating", "Released"]),

                # Random birth date within the last 5 years
                date_of_birth=fake.date_between(start_date="-5y", end_date="-1y"),

                # Random arrival date within the last year.
                arrival_date=fake.date_between(start_date="-1y", end_date="today"),
            )
            otters_to_create.append(otter)

        # Insert all otters in one operation.
        Otter.objects.bulk_create(otters_to_create)

        self.stdout.write(self.style.SUCCESS("Otter records created."))

        # Re-query the database so we can use the saved otter records.
        all_otters = Otter.objects.all()

        # A list to store health assessments before bulk creation.
        assessments_to_create = []

        # Create 3 to 6 health assessments per otter.
        for otter in all_otters:
            num_records = random.randint(3, 6)

            # Start from the otter's current weight if available.
            # Fall back to a realistic random weight if needed.
            base_weight = float(otter.weight_kg) if otter.weight_kg is not None else random.uniform(4.0, 8.0)

            # Give each otter a health trend over time.
            trend = random.choice(["improving", "declining", "stable"])

            # Create several assessments over time.
            for i in range(num_records):
                # Space assessments out in the past.
                assessment_date = date.today() - timedelta(days=(num_records - i) * 14)

                # Simulate changing weight and condition over time.
                if trend == "improving":
                    weight = base_weight + (i * random.uniform(0.10, 0.30))
                    condition = random.choice(["Fair", "Good"])
                    notes = "Health improving over time with steady recovery."

                elif trend == "declining":
                    weight = base_weight - (i * random.uniform(0.10, 0.30))
                    condition = random.choice(["Poor", "Fair"])
                    notes = "Health decline observed; monitoring required."

                else:
                    weight = base_weight + random.uniform(-0.20, 0.20)
                    condition = "Good"
                    notes = "Stable health observed across assessments."

                # Keep the generated weight within a realistic range.
                weight = max(Decimal("3.50"), min(Decimal(str(round(weight, 2))), Decimal("12.00")))

                assessment = HealthAssessment(
                    otter=otter,
                    assessment_date=assessment_date,
                    weight_kg=weight,
                    temperature=Decimal(str(round(random.uniform(36.0, 39.0), 2))),
                    general_condition=condition,
                    notes=notes,
                )

                assessments_to_create.append(assessment)

        # Insert all assessments in one operation.
        HealthAssessment.objects.bulk_create(assessments_to_create)

        self.stdout.write(self.style.SUCCESS("Health assessment records created."))
        self.stdout.write(self.style.SUCCESS("Seed process completed successfully."))