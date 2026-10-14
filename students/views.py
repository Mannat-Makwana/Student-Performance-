"""Views for student and marks CRUD, analytics, and predictions."""

import base64
from io import BytesIO

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from sklearn.linear_model import LinearRegression

from .analytics import build_charts, calculate_summary, marks_dataframe, subject_averages
from .forms import MarksForm, StudentForm
from .models import Marks, Student


def dashboard(request):
    """Render class performance statistics, subject averages, and charts."""
    frame = marks_dataframe(Marks.objects.all())
    averages = subject_averages(frame)
    average_rows = averages.to_dict(orient="records")
    context = {
        **calculate_summary(frame),
        **build_charts(frame, averages),
        "subject_averages": average_rows,
    }
    return render(request, "students/dashboard.html", context)


def student_list(request):
    """Show paginated students and their mark counts."""
    paginator = Paginator(Student.objects.all().prefetch_related("marks"), 10)
    students = paginator.get_page(request.GET.get("page"))
    return render(request, "students/student_list.html", {"students": students})


def student_create(request):
    """Create a student after ModelForm validation."""
    form = StudentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        student = form.save()
        messages.success(request, f"Student {student.name} was added.")
        return redirect("students:list")
    return render(request, "students/student_form.html", {"form": form, "title": "Add Student"})


def student_update(request, pk):
    """Update a student's details after ModelForm validation."""
    student = get_object_or_404(Student, pk=pk)
    form = StudentForm(request.POST or None, instance=student)
    if request.method == "POST" and form.is_valid():
        student = form.save()
        messages.success(request, f"Student {student.name} was updated.")
        return redirect("students:list")
    return render(
        request,
        "students/student_form.html",
        {"form": form, "title": "Edit Student", "student": student},
    )


@require_POST
def student_delete(request, pk):
    """Delete a student and cascade-delete associated marks."""
    student = get_object_or_404(Student, pk=pk)
    student_name = student.name
    student.delete()
    messages.success(request, f"Student {student_name} and their marks were deleted.")
    return redirect("students:list")


def marks_list(request):
    """Show all mark records with student and semester details."""
    marks = Marks.objects.select_related("student")
    return render(request, "students/marks_list.html", {"marks": marks})


def marks_create(request):
    """Create a mark record after range validation."""
    form = MarksForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        mark = form.save()
        messages.success(request, f"Marks for {mark.student.name} were added.")
        return redirect("students:marks_list")
    return render(request, "students/marks_form.html", {"form": form, "title": "Add Marks"})


def marks_update(request, pk):
    """Update a mark record after range validation."""
    mark = get_object_or_404(Marks, pk=pk)
    form = MarksForm(request.POST or None, instance=mark)
    if request.method == "POST" and form.is_valid():
        mark = form.save()
        messages.success(request, f"Marks for {mark.student.name} were updated.")
        return redirect("students:marks_list")
    return render(
        request,
        "students/marks_form.html",
        {"form": form, "title": "Edit Marks", "mark": mark},
    )


@require_POST
def marks_delete(request, pk):
    """Delete one mark record."""
    mark = get_object_or_404(Marks, pk=pk)
    student_name = mark.student.name
    mark.delete()
    messages.success(request, f"Marks for {student_name} were deleted.")
    return redirect("students:marks_list")


def _prediction_chart(regression, minimum, maximum, entered_score, predicted_score):
    """Render the regression line and entered prediction as a base64 image."""
    x_values = np.linspace(minimum, maximum, 100).reshape(-1, 1)
    figure, axis = plt.subplots(figsize=(7, 4))
    axis.plot(
        x_values,
        regression.predict(x_values),
        color="#4361ee",
        label="Linear regression",
    )
    axis.scatter(
        [entered_score],
        [predicted_score],
        color="#e76f51",
        s=70,
        label="Your prediction",
        zorder=3,
    )
    axis.set_xlabel("Internal marks")
    axis.set_ylabel("Predicted final marks")
    axis.set_xlim(0, 50)
    axis.set_ylim(0, 100)
    axis.legend()
    axis.set_title("Internal-to-Final Marks Prediction")
    image_buffer = BytesIO()
    figure.savefig(image_buffer, format="png", bbox_inches="tight", dpi=120)
    plt.close(figure)
    return base64.b64encode(image_buffer.getvalue()).decode("ascii")


def predict(request):
    """Fit linear regression to existing marks and predict a final score."""
    records = Marks.objects.values_list("internal_marks", "final_marks")
    result = None
    chart = None
    error = None

    if len(records) < 2:
        error = "Add at least two marks records before making a prediction."
    else:
        features = np.array([row[0] for row in records], dtype=float).reshape(-1, 1)
        targets = np.array([row[1] for row in records], dtype=float)
        regression = LinearRegression().fit(features, targets)
        if request.method == "POST":
            try:
                entered_score = float(request.POST.get("internal_marks", ""))
                if not np.isfinite(entered_score) or not 0 <= entered_score <= 50:
                    raise ValueError
            except ValueError:
                error = "Enter a valid internal mark between 0 and 50."
            else:
                predicted_score = float(
                    np.clip(regression.predict([[entered_score]])[0], 0, 100)
                )
                result = round(predicted_score, 2)
                chart = _prediction_chart(
                    regression,
                    float(features.min()),
                    float(features.max()),
                    entered_score,
                    predicted_score,
                )

    return render(
        request,
        "students/predict.html",
        {
            "result": result,
            "chart": chart,
            "error": error,
            "internal_marks": request.POST.get("internal_marks", ""),
            "can_predict": len(Marks.objects.all()) >= 2,
        },
    )
