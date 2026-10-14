"""Application configuration for student records."""

from django.apps import AppConfig


class StudentsConfig(AppConfig):
    """Configure the students application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "students"

