from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path

from config.settings import settings

TEMPLATE_DIR = Path(__file__).parent / settings.templates


env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=select_autoescape(["html", "xml"]),
)


def generate_html_report(
        manager_name: str,
        project_hours_df,
        avg_duration_df,
        variance_df,
        monthly_df,
        charts: dict
) -> str:
    """
    Renders the HTML report for a manager using Jinja2.
    """

    template = env.get_template("report.html")

    html = template.render(
        manager_name=manager_name,
        project_hours=project_hours_df.to_dict(orient="records"),
        avg_duration=(
            avg_duration_df.to_dict(orient="records")[0]
            if not avg_duration_df.empty else None
        ),
        variance=variance_df.to_dict(orient="records"),
        monthly=monthly_df.to_dict(orient="records"),
        charts=charts
    )

    return html
