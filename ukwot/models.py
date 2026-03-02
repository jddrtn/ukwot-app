from django.db import models

from django.db import models


class Species(models.Model):
    species_id = models.AutoField(primary_key=True)
    common_name = models.CharField(max_length=100)
    scientific_name = models.CharField(max_length=150)
    conservation_status = models.CharField(max_length=50)
    average_lifespan = models.PositiveSmallIntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "species"

    def __str__(self) -> str:
        return self.common_name


class RescueCase(models.Model):
    rescue_id = models.AutoField(primary_key=True)
    rescue_date = models.DateField()
    rescue_location = models.CharField(max_length=255)
    rescue_circumstances = models.TextField()
    rescue_condition = models.CharField(max_length=100, null=True, blank=True)

    # Exists + NOT NULL in schema, FK to staff(staff_id)
    # keep it as an int for now
    staff_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = "rescue_case"

    def __str__(self) -> str:
        return f"Rescue {self.rescue_id} ({self.rescue_date})"


class Otter(models.Model):
    otter_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=50, default="Rescued")
    arrival_date = models.DateField()

    species = models.ForeignKey(
        Species,
        on_delete=models.PROTECT,
        db_column="species_id",
    )

    rescue = models.ForeignKey(
        RescueCase,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="rescue_id",
    )

    # In DB: location_id INT NULL FK to location(location_id)
    location_id = models.IntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "otter"

    def __str__(self) -> str:
        return self.name
