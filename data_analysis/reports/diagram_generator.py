import sys

import matplotlib.pyplot as plt
from pathlib import Path

from config.settings import settings

BASE_PATH = Path(__file__).parent / settings.diagrams_path

def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def plot_monthly_hours(df, manager_id):
    """
    Create a line chart of monthly total hours for all projects (summed).
    """
    if df.empty:
        return None

    out_dir = BASE_PATH / Path(str(manager_id))
    ensure_dir(out_dir)

    monthly = df.groupby("month")["totalMonthlyHours"].sum().reset_index()

    monthly = monthly.sort_values("month")

    plt.figure(figsize=(9, 4))
    plt.plot(monthly["month"], monthly["totalMonthlyHours"])
    plt.title("Monthly Total Hours")
    plt.xlabel("Month")
    plt.ylabel("Hours Worked")
    plt.xticks(rotation=45)
    plt.tight_layout()

    file_path = out_dir / "monthly_hours.png"
    plt.savefig(file_path, dpi=120)
    plt.close()

    return file_path.as_uri()


def plot_duration_variance(df, manager_id):
    """
    Bar chart of duration variance for each project.
    """
    if df.empty:
        return None

    out_dir = BASE_PATH / Path(str(manager_id))
    ensure_dir(out_dir)

    df_sorted = df.sort_values("durationVarianceDays", ascending=True)

    plt.figure(figsize=(10, 5))
    plt.bar(df_sorted["projectName"], df_sorted["durationVarianceDays"])
    plt.title("Project Duration Variance (Days)")
    plt.xlabel("Project")
    plt.ylabel("Variance (Actual - Planned)")
    plt.xticks(rotation=45)
    plt.tight_layout()

    file_path = out_dir / "duration_variance.png"
    plt.savefig(file_path, dpi=120)
    plt.close()

    return file_path.as_uri()


def plot_employee_hours(df, manager_id):
    """
    Stacked bar chart: total hours per project per employee.
    """
    if df.empty:
        return None

    out_dir = BASE_PATH / Path(str(manager_id))
    ensure_dir(out_dir)

    pivot = df.pivot_table(
        index="projectName",
        columns="userName",
        values="totalHours",
        aggfunc="sum",
        fill_value=0
    )

    plt.figure(figsize=(12, 6))
    pivot.plot(kind="bar", stacked=True)
    plt.title("Employee Hours per Project")
    plt.xlabel("Project")
    plt.ylabel("Hours")
    plt.xticks(rotation=45)
    plt.tight_layout()

    file_path = out_dir / "employee_hours.png"
    plt.savefig(file_path, dpi=120)
    plt.close()

    return file_path.as_uri()


def generate_all_charts(
        project_hours_df,
        variance_df,
        monthly_df,
        manager_id,
):
    """
    Generate all charts for a given manager and return a dict of file paths.
    """
    return {
        "monthly_hours": plot_monthly_hours(monthly_df, manager_id),
        "duration_variance": plot_duration_variance(variance_df, manager_id),
        "employee_hours": plot_employee_hours(project_hours_df, manager_id),
    }