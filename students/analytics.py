"""Pandas analysis and server-rendered charts for student performance."""

import base64
from io import BytesIO

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


def marks_dataframe(queryset):
    """Load mark records into a DataFrame with the associated student names."""
    rows = queryset.select_related("student").values(
        "student__name", "subject", "internal_marks", "final_marks", "semester"
    )
    frame = pd.DataFrame.from_records(rows)
    if frame.empty:
        return pd.DataFrame(
            columns=[
                "student__name",
                "subject",
                "internal_marks",
                "final_marks",
                "semester",
            ]
        )
    return frame


def calculate_summary(frame):
    """Calculate class-level final-score statistics and pass percentage."""
    if frame.empty:
        return {
            "class_average": 0.0,
            "highest_score": 0,
            "lowest_score": 0,
            "topper_name": "—",
            "pass_percentage": 0.0,
            "total_records": 0,
            "pass_count": 0,
            "fail_count": 0,
        }

    final_scores = frame["final_marks"]
    top_row = frame.loc[final_scores.idxmax()]
    pass_count = int((final_scores >= 40).sum())
    total_records = len(frame)
    return {
        "class_average": round(float(final_scores.mean()), 2),
        "highest_score": int(final_scores.max()),
        "lowest_score": int(final_scores.min()),
        "topper_name": str(top_row["student__name"]),
        "pass_percentage": round(pass_count / total_records * 100, 2),
        "total_records": total_records,
        "pass_count": pass_count,
        "fail_count": total_records - pass_count,
    }


def subject_averages(frame):
    """Return subject-wise average final marks as a sorted DataFrame."""
    if frame.empty:
        return pd.DataFrame(columns=["subject", "average"])
    return (
        frame.groupby("subject", as_index=False)["final_marks"]
        .mean()
        .rename(columns={"final_marks": "average"})
        .sort_values("subject")
        .reset_index(drop=True)
    )


def _figure_to_base64(figure):
    """Encode a Matplotlib figure as a PNG data URI payload."""
    image_buffer = BytesIO()
    figure.savefig(image_buffer, format="png", bbox_inches="tight", dpi=120)
    plt.close(figure)
    return base64.b64encode(image_buffer.getvalue()).decode("ascii")


def build_charts(frame, averages):
    """Build subject-average, final-score histogram, and pass/fail charts."""
    bar_figure, bar_axis = plt.subplots(figsize=(8, 4))
    if averages.empty:
        bar_axis.text(0.5, 0.5, "No marks recorded", ha="center", va="center")
        bar_axis.set_axis_off()
    else:
        bar_axis.bar(averages["subject"], averages["average"], color="#4361ee")
        bar_axis.set_ylabel("Average final marks")
        bar_axis.set_ylim(0, 100)
        bar_axis.tick_params(axis="x", rotation=30)
    bar_axis.set_title("Subject-wise Average")

    histogram_figure, histogram_axis = plt.subplots(figsize=(8, 4))
    histogram_axis.hist(
        frame["final_marks"] if not frame.empty else [],
        bins=10,
        range=(0, 100),
        color="#2a9d8f",
        edgecolor="white",
    )
    histogram_axis.set_title("Final Marks Distribution")
    histogram_axis.set_xlabel("Final marks")
    histogram_axis.set_ylabel("Number of records")

    pie_figure, pie_axis = plt.subplots(figsize=(5, 4))
    summary = calculate_summary(frame)
    counts = [summary["pass_count"], summary["fail_count"]]
    if sum(counts) == 0:
        pie_axis.text(0.5, 0.5, "No marks recorded", ha="center", va="center")
        pie_axis.set_axis_off()
    else:
        pie_axis.pie(
            counts,
            labels=["Pass (≥ 40)", "Fail (< 40)"],
            colors=["#2a9d8f", "#e76f51"],
            autopct="%1.1f%%",
            startangle=90,
        )
    pie_axis.set_title("Pass vs Fail")

    return {
        "subject_chart": _figure_to_base64(bar_figure),
        "histogram_chart": _figure_to_base64(histogram_figure),
        "pass_fail_chart": _figure_to_base64(pie_figure),
    }

