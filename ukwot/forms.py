# ukwot/forms.py

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Otter


class OtterForm(forms.ModelForm):
    """
    Otter form with:
    - Dropdowns for gender and status
    - Date validation to prevent future dates
    """

    # Explicit choices for gender (matches DB ENUM values)
    GENDER_CHOICES = [
        ("Male", "Male"),
        ("Female", "Female"),
        ("Unknown", "Unknown"),
    ]

    # Explicit choices for status (matches DB ENUM values)
    STATUS_CHOICES = [
        ("Rescued", "Rescued"),
        ("Rehabilitating", "Rehabilitating"),
        ("Released", "Released"),
    ]

    # Override model fields with dropdown widgets/choices
    gender = forms.ChoiceField(choices=GENDER_CHOICES)
    status = forms.ChoiceField(choices=STATUS_CHOICES)

    # HTML5 date picker widgets
    date_of_birth = forms.DateField(
        required=False,  # DB allows null
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
            "rescue",
        ]

    def clean_date_of_birth(self):
        """
        Date of birth:
        - Optional
        - Cannot be in the future
        """
        dob = self.cleaned_data.get("date_of_birth")
        if dob and dob > timezone.localdate():
            raise ValidationError("Date of birth cannot be in the future.")
        return dob

    def clean_arrival_date(self):
        """
        Arrival date:
        - Required
        - Cannot be in the future
        """
        arrival = self.cleaned_data.get("arrival_date")
        if arrival and arrival > timezone.localdate():
            raise ValidationError("Arrival date cannot be in the future.")
        return arrival

    # ukwot/forms.py (inside OtterForm)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        today = timezone.localdate().isoformat()

        # Prevent choosing future dates in the date picker UI
        self.fields["date_of_birth"].widget.attrs["max"] = today
        self.fields["arrival_date"].widget.attrs["max"] = today