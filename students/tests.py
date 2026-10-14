"""Tests for models, analytics, and student-facing views."""

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from .analytics import calculate_summary, marks_dataframe, subject_averages
from .models import Marks, Student


class StudentModelTests(TestCase):
    """Check student and mark model constraints and relationships."""

    def setUp(self):
        """Create a student to use in model tests."""
        self.student = Student.objects.create(
            name="Aanya Patel",
            roll_no="CS001",
            email="aanya@example.edu",
            department="Computer Science",
        )

    def test_roll_number_is_unique(self):
        """Duplicate roll numbers are rejected by the database."""
        with self.assertRaises(IntegrityError), transaction.atomic():
            Student.objects.create(
                name="Another Student",
                roll_no="CS001",
                email="other@example.edu",
                department="Computer Science",
            )

    def test_marks_validate_score_range(self):
        """Model validation rejects marks above the allowed range."""
        mark = Marks(
            student=self.student,
            subject="Mathematics",
            internal_marks=51,
            final_marks=80,
            semester=1,
        )
        with self.assertRaises(ValidationError):
            mark.full_clean()

    def test_deleting_student_cascades_to_marks(self):
        """Deleting a student removes their associated mark rows."""
        mark = Marks.objects.create(
            student=self.student,
            subject="Mathematics",
            internal_marks=40,
            final_marks=82,
            semester=1,
        )
        self.student.delete()
        self.assertFalse(Marks.objects.filter(pk=mark.pk).exists())


class AnalyticsTests(TestCase):
    """Verify DataFrame analysis and summary calculations."""

    def setUp(self):
        """Create marks spanning pass and fail outcomes."""
        self.student = Student.objects.create(
            name="Aanya Patel",
            roll_no="CS001",
            email="aanya@example.edu",
            department="Computer Science",
        )
        Marks.objects.create(
            student=self.student,
            subject="Math",
            internal_marks=40,
            final_marks=80,
            semester=1,
        )
        Marks.objects.create(
            student=self.student,
            subject="Science",
            internal_marks=30,
            final_marks=30,
            semester=1,
        )

    def test_summary_reports_class_statistics(self):
        """Summary uses final marks and treats 40 as a pass."""
        summary = calculate_summary(marks_dataframe(Marks.objects.all()))
        self.assertEqual(summary["class_average"], 55.0)
        self.assertEqual(summary["highest_score"], 80)
        self.assertEqual(summary["lowest_score"], 30)
        self.assertEqual(summary["topper_name"], "Aanya Patel")
        self.assertEqual(summary["pass_percentage"], 50.0)

    def test_subject_averages_are_returned(self):
        """Subject means are grouped and returned in the analytics table."""
        frame = marks_dataframe(Marks.objects.all())
        averages = subject_averages(frame)
        self.assertEqual(averages.to_dict(orient="records"), [
            {"subject": "Math", "average": 80.0},
            {"subject": "Science", "average": 30.0},
        ])

    def test_empty_summary_is_safe(self):
        """An empty marks collection yields neutral dashboard statistics."""
        from .analytics import calculate_summary
        import pandas as pd

        self.assertEqual(calculate_summary(pd.DataFrame()), {
            "class_average": 0.0,
            "highest_score": 0,
            "lowest_score": 0,
            "topper_name": "—",
            "pass_percentage": 0.0,
            "total_records": 0,
            "pass_count": 0,
            "fail_count": 0,
        })


class StudentViewTests(TestCase):
    """Exercise dashboard and student creation view behavior."""

    def test_dashboard_loads_with_empty_database(self):
        """The dashboard responds successfully when no marks exist."""
        response = self.client.get(reverse("students:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Student Performance Dashboard")
        self.assertContains(response, "data:image/png;base64,")

    def test_create_student_view_saves_valid_submission(self):
        """Valid student form posts create a student and redirect."""
        response = self.client.post(
            reverse("students:create"),
            {
                "name": "Aanya Patel",
                "roll_no": "CS001",
                "email": "aanya@example.edu",
                "department": "Computer Science",
            },
        )
        self.assertRedirects(response, reverse("students:list"))
        self.assertTrue(Student.objects.filter(roll_no="CS001").exists())

    def test_predict_view_reports_insufficient_data(self):
        """Prediction is unavailable until at least two marks exist."""
        response = self.client.get(reverse("students:predict"))
        self.assertContains(response, "Add at least two marks records")

    def test_predict_view_returns_score_when_training_data_exists(self):
        """Prediction trains on stored marks and displays a predicted score."""
        student = Student.objects.create(
            name="Aanya Patel",
            roll_no="CS001",
            email="aanya@example.edu",
            department="Computer Science",
        )
        Marks.objects.create(
            student=student,
            subject="Math",
            internal_marks=20,
            final_marks=45,
            semester=1,
        )
        Marks.objects.create(
            student=student,
            subject="Science",
            internal_marks=40,
            final_marks=85,
            semester=1,
        )
        response = self.client.post(
            reverse("students:predict"), {"internal_marks": "30"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Predicted final score")
        self.assertContains(response, "data:image/png;base64,")
