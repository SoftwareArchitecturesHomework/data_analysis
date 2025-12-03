import base64
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from config.settings import settings
from dto.report_dto import ReportDTO
from reports.diagram_generator import (
    generate_all_charts
)

from reports.html_generator import generate_html_report
from reports.pdf_generator import generate_pdf_from_html

from data.queries import (
    get_project_employee_total_hours_by_manager,
    get_avg_completed_project_duration_hours_by_manager,
    get_project_duration_variance_hours_by_manager,
    get_monthly_project_hours_hours_by_manager,
    fetch_manager
)


def generate_manager_report(manager_id: int):

    manager_name = fetch_manager(manager_id)

    df_hours = get_project_employee_total_hours_by_manager(manager_id)
    df_avg = get_avg_completed_project_duration_hours_by_manager(manager_id)
    df_variance = get_project_duration_variance_hours_by_manager(manager_id)
    df_monthly = get_monthly_project_hours_hours_by_manager(manager_id)

    charts = generate_all_charts(df_hours, df_variance, df_monthly, manager_id)

    base64_charts = {}

    for key, path in charts.items():
        if not path:
            continue
        try:
            parsed_uri = urlparse(path)
            path_segment = parsed_uri.path
            # Keep the leading slash for absolute paths
            local_path = Path(path_segment) if path_segment.startswith('/') else Path(path_segment[1:])
            with open(local_path, "rb") as fh:
                data = fh.read()
        except Exception:
            data = ""

        if data:
            # Convert raw bytes (data) into a Base64 string (bytes)
            base64_string = base64.b64encode(data).decode('utf-8')
        else:
            base64_string = b""
        base64_charts[key] = base64_string

    html = generate_html_report(
        manager_name=manager_name,
        project_hours_df=df_hours,
        avg_duration_df=df_avg,
        variance_df=df_variance,
        monthly_df=df_monthly,
        charts=base64_charts
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_path = settings.pdf_path + f"/manager_{manager_id}_{timestamp}.pdf"

    generate_pdf_from_html(html, pdf_path)

    return ReportDTO(
        manager_id=manager_id,
        manager_name=manager_name,
        html=html,
        pdf_path=str(pdf_path),
        charts=charts
    )