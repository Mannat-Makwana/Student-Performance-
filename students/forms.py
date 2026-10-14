"""Model forms and field validation for student records."""

from django import forms

from .models import Marks, Student


class StudentForm(forms.ModelForm):
    """Validate and edit student details."""

    def __init__(self, *args, **kwargs):
        """Apply the shared Bootstrap control styling to form widgets."""
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

    class Meta:
        model = Student
        fields = ["name", "roll_no", "email", "department"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "e.g. Aanya Patel"}),
            "roll_no": forms.TextInput(attrs={"placeholder": "e.g. CS2026001"}),
            "email": forms.EmailInput(attrs={"placeholder": "student@example.com"}),
            "department": forms.TextInput(attrs={"placeholder": "e.g. Computer Science"}),
        }


class MarksForm(forms.ModelForm):
    """Validate marks and provide a student selector."""

    def __init__(self, *args, **kwargs):
        """Style text, numeric, and select controls consistently."""
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = (
                "form-select" if isinstance(field.widget, forms.Select) else "form-control"
            )

    class Meta:
        model = Marks
        fields = ["student", "subject", "internal_marks", "final_marks", "semester"]
        widgets = {
            "student": forms.Select(),
            "subject": forms.TextInput(attrs={"placeholder": "e.g. Data Structures"}),
            "internal_marks": forms.NumberInput(attrs={"min": 0, "max": 50}),
            "final_marks": forms.NumberInput(attrs={"min": 0, "max": 100}),
            "semester": forms.NumberInput(attrs={"min": 1, "max": 12}),
        }

    def clean_internal_marks(self):
        """Reject internal scores outside the supported range."""
        value = self.cleaned_data["internal_marks"]
        if not 0 <= value <= 50:
            raise forms.ValidationError("Internal marks must be between 0 and 50.")
        return value

    def clean_final_marks(self):
        """Reject final scores outside the supported range."""
        value = self.cleaned_data["final_marks"]
        if not 0 <= value <= 100:
            raise forms.ValidationError("Final marks must be between 0 and 100.")
        return value
