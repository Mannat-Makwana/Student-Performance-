"""URL patterns for the students application."""

from django.urls import path

from . import views

app_name = "students"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("students/", views.student_list, name="list"),
    path("students/add/", views.student_create, name="create"),
    path("students/<int:pk>/edit/", views.student_update, name="update"),
    path("students/<int:pk>/delete/", views.student_delete, name="delete"),
    path("marks/", views.marks_list, name="marks_list"),
    path("marks/add/", views.marks_create, name="marks_create"),
    path("marks/<int:pk>/edit/", views.marks_update, name="marks_update"),
    path("marks/<int:pk>/delete/", views.marks_delete, name="marks_delete"),
    path("predict/", views.predict, name="predict"),
]

