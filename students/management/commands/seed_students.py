"""Seed the database with sample students and realistic marks."""

import random

from django.core.management.base import BaseCommand
from django.db import transaction

from students.models import Marks, Student


class Command(BaseCommand):
    """Create 20 students and marks for several subjects."""

    help = "Seed the database with 20 sample students and realistic marks."

    @transaction.atomic
    def handle(self, **options):
        """Create seed records unless sample roll numbers already exist."""
        first_names = [
            "Aanya", "Aarav", "Diya", "Ishaan", "Kavya", "Krish", "Meera",
            "Neel", "Pari", "Reyansh", "Riya", "Saanvi", "Shaurya", "Tara",
            "Vihaan", "Yash", "Anaya", "Dev", "Ira", "Kabir",
        ]
        last_names = [
            "Patel", "Shah", "Mehta", "Joshi", "Desai", "Rao", "Trivedi",
            "Kapoor", "Nair", "Kulkarni", "Iyer", "Singh", "Pillai", "Gandhi",
            "Verma", "Chopra", "Mistry", "Bose", "Sethi", "Malhotra",
        ]
        departments = ["Computer Science", "Information Technology", "Electronics"]
        subjects = ["Mathematics", "Data Structures", "Database Systems", "Networks"]
        created_students = 0
        created_marks = 0

        for index, (first_name, last_name) in enumerate(
            zip(first_names, last_names), start=1
        ):
            roll_no = f"SP{index:04d}"
            student, created = Student.objects.get_or_create(
                roll_no=roll_no,
                defaults={
                    "name": f"{first_name} {last_name}",
                    "email": f"{first_name.lower()}.{last_name.lower()}@example.edu",
                    "department": departments[(index - 1) % len(departments)],
                },
            )
            if created:
                created_students += 1
            for semester in (1, 2):
                for subject in subjects:
                    _, mark_created = Marks.objects.get_or_create(
                        student=student,
                        subject=subject,
                        semester=semester,
                        defaults={
                            "internal_marks": random.randint(24, 49),
                            "final_marks": random.randint(35, 98),
                        },
                    )
                    created_marks += int(mark_created)

        if options.get("verbosity", 1) > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Seed complete: {created_students} students and "
                    f"{created_marks} marks created."
                )
            )
