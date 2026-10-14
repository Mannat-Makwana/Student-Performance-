"""Database models for students and their marks."""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Student(models.Model):
    """A student whose academic performance is tracked."""

    name = models.CharField(max_length=120)
    roll_no = models.CharField(max_length=30, unique=True)
    email = models.EmailField()
    department = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name", "roll_no"]

    def __str__(self):
        """Return a readable student identifier."""
        return f"{self.name} ({self.roll_no})"


class Marks(models.Model):
    """Internal and final marks for one student in one subject and semester."""

    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="marks"
    )
    subject = models.CharField(max_length=100)
    internal_marks = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(50)]
    )
    final_marks = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    semester = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )

    class Meta:
        ordering = ["student__name", "semester", "subject"]

    def __str__(self):
        """Return a readable subject and student description."""
        return f"{self.student.name}: {self.subject} (Semester {self.semester})"

