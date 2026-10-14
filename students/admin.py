"""Admin registrations for student performance records."""

from django.contrib import admin

from .models import Marks, Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Admin list configuration for students."""

    list_display = ("name", "roll_no", "email", "department", "created_at")
    search_fields = ("name", "roll_no", "email")


@admin.register(Marks)
class MarksAdmin(admin.ModelAdmin):
    """Admin list configuration for marks."""

    list_display = ("student", "subject", "semester", "internal_marks", "final_marks")
    list_filter = ("semester", "subject")
    search_fields = ("student__name", "student__roll_no", "subject")

