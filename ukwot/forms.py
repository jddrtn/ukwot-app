from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Otter, HealthAssessment


class OtterForm(forms.ModelForm):
    """
    Existing otter form.
    """

    GENDER_CHOICES = [
        ("Male", "Male"),
        ("Female", "Female"),
        ("Unknown", "Unknown"),
    ]

    STATUS_CHOICES = [
        ("Rescued", "Rescued"),
        ("Rehabilitating", "Rehabilitating"),
        ("Released", "Released"),
    ]

    gender = forms.ChoiceField(choices=GENDER_CHOICES)
    status = forms.ChoiceField(choices=STATUS_CHOICES)

    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    arrival_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    class Meta:
        model = Otter
        fields = [
            "name",
            "species",
            "gender",
            "weight_kg",
            "status",
            "date_of_birth",
            "arrival_date",
        ]

    def __init__(self, *args, **kwargs):
        """
        Add date picker max attributes for better UX.
        """
        super().__init__(*args, **kwargs)
        today = timezone.localdate().isoformat()
        self.fields["date_of_birth"].widget.attrs["max"] = today
        self.fields["arrival_date"].widget.attrs["max"] = today

    def clean_date_of_birth(self):
        """
        Prevent future dates of birth.
        """
        dob = self.cleaned_data.get("date_of_birth")
        if dob and dob > timezone.localdate():
            raise ValidationError("Date of birth cannot be in the future.")
        return dob

    def clean_arrival_date(self):
        """
        Prevent future arrival dates.
        """
        arrival = self.cleaned_data.get("arrival_date")
        if arrival and arrival > timezone.localdate():
            raise ValidationError("Arrival date cannot be in the future.")
        return arrival


class MedicalRecordForm(forms.ModelForm):
    """
    Form for creating/editing medical records.
    """

    GENERAL_CONDITION_CHOICES = [
        ("Fair", "Fair"),
        ("Good", "Good"),
        ("Poor", "Poor"),
    ]

    otter = forms.ModelChoiceField(
        queryset=Otter.objects.all().order_by("name"),
        empty_label="Select an otter",
    )

    assessment_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    general_condition = forms.ChoiceField(
        choices=GENERAL_CONDITION_CHOICES,
    )

    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 4}),
    )

    class Meta:
        model = HealthAssessment
        fields = [
            "otter",
            "assessment_date",
            "weight_kg",
            "general_condition",
            "notes",
        ]

    def __init__(self, *args, **kwargs):
        """
        Add a max date so future dates cannot be selected in the UI.
        """
        super().__init__(*args, **kwargs)
        today = timezone.localdate().isoformat()
        self.fields["assessment_date"].widget.attrs["max"] = today

    def clean_assessment_date(self):
        """
        Prevent future assessment dates.
        """
        value = self.cleaned_data.get("assessment_date")
        if value and value > timezone.localdate():
            raise ValidationError("Assessment date cannot be in the future.")
        return value