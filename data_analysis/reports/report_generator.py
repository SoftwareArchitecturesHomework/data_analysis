from datetime import datetime

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

    html = generate_html_report(
        manager_name=manager_name,
        project_hours_df=df_hours,
        avg_duration_df=df_avg,
        variance_df=df_variance,
        monthly_df=df_monthly,
        charts=charts
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