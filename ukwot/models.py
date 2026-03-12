from django.db import models


class Species(models.Model):
    """
    Existing unmanaged model mapped to the species table.
    """
    species_id = models.AutoField(primary_key=True)
    common_name = models.CharField(max_length=100)
    scientific_name = models.CharField(max_length=150)
    conservation_status = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = "species"

    def __str__(self):
        """
        Human-readable label for dropdowns.
        """
        return self.common_name


class Otter(models.Model):
    """
    Existing unmanaged model mapped to the otter table.
    """
    otter_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=20)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=50)
    arrival_date = models.DateField()

    species = models.ForeignKey(
        Species,
        on_delete=models.DO_NOTHING,
        db_column="species_id",
        related_name="otters",
    )

    class Meta:
        managed = False
        db_table = "otter"

    def __str__(self):
        """
        Show the otter name in dropdowns.
        """
        return self.name


class HealthAssessment(models.Model):
    """
    Unmanaged model mapped to the health_assessment table.
    """
    assessment_id = models.AutoField(primary_key=True)

    otter = models.ForeignKey(
        Otter,
        on_delete=models.DO_NOTHING,
        db_column="otter_id",
        related_name="health_assessments",
    )

    assessment_date = models.DateField()
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    temperature = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    general_condition = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "health_assessment"

    def __str__(self):
        """
        Human-readable label for a medical record.
        """
        return f"Assessment {self.assessment_id} - {self.otter.name}"

    @property
    def effective_weight_kg(self):
        """
        Use the assessment weight if present; otherwise fall back
        to the original otter table weight.
        """
        return self.weight_kg if self.weight_kg is not None else self.otter.weight_kg