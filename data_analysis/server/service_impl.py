import logging
import os
from pathlib import Path
from urllib.parse import urlparse
import base64

from config.settings import settings
from data.queries import fetch_manager, fetch_all_manager_ids
from server.generated import report_pb2, report_pb2_grpc

from reports.report_generator import generate_manager_report

logger = logging.getLogger(__name__)


def clean_temp():
    try:
        for item_name in os.listdir(settings.pdf_path):
            os.remove(os.path.join(settings.pdf_path, item_name))
        print(f"Cleaned up temporary files: {settings.pdf_path}")
    except OSError as e:
        print(f"Error: Failed to delete temporary file {settings.pdf_path}. Error: {e}")


class ReportServiceServicer(report_pb2_grpc.ReportServiceServicer):
    """
    gRPC service implementation for report generation.
    """

    def __init__(self):
        super().__init__()

    def _build_manager_report_package(self, manager_id: int, manager_name: str):
        """
        Calls the pipeline and returns a dict with html, pdf bytes and charts list.
        Expected pipeline output (dict):
            {
              "manager_id": int,
              "manager_name": str,
              "html": "<html>...</html>",
              "pdf_path": "/abs/path/to/pdf",
              "charts": {"monthly_hours": "/path/to.png", ...}
            }
        """
        result = generate_manager_report(manager_id=manager_id)

        # html string
        html = result.html

        # read pdf bytes
        pdf_path = result.pdf_path
        pdf_bytes = b""
        if pdf_path:
            try:
                with open(pdf_path, "rb") as fh:
                    pdf_bytes = fh.read()
            except Exception as exc:
                logger.exception("Failed to read generated pdf at %s: %s", pdf_path, exc)

        # read chart files (if any)
        charts_out = []
        charts = result.charts or {}
        for key, path in charts.items():
            if not path:
                continue
            try:
                parsed_uri = urlparse(path)
                path_segment = parsed_uri.path
                local_path = Path(path_segment[1:])
                with open(local_path, "rb") as fh:
                    data = fh.read()
            except Exception:
                logger.exception("Failed to read chart file %s", path)
                data = b""

            if data:
                # Convert raw bytes (data) into a Base64 string (bytes)
                base64_data = base64.b64encode(data)
            else:
                base64_data = b""
            # ----------------------------------------------

            charts_out.append(
                report_pb2.Chart(
                    filename=path.split("/")[-1],
                    title=key,
                    # Pass the Base64 bytes to the Protobuf message
                    data=base64_data
                )
            )

        return {
            "html": html,
            "pdf": pdf_bytes,
            "charts": charts_out
        }

    def _generate_manager_report_message(self, manager_id: int, manager_name: str) -> report_pb2.ManagerReport:

        packaged = self._build_manager_report_package(manager_id, manager_name)

        # 2. Construct the ManagerReport response message
        mr = report_pb2.ManagerReport(
            manager_id=manager_id,
            manager_name=manager_name,
            # Access attributes using dictionary keys
            html=packaged["html"],
            pdf=packaged["pdf"],
        )

        # 3. Add charts to the report message
        for chart in packaged["charts"]:
            mr.charts.add(
                filename=chart.filename,
                title=chart.title,
                data=chart.data
            )

        return mr

    def GetManagerHTML(self, request, context):
        manager_id = int(request.manager_id)
        manager_name = fetch_manager(manager_id)
        packaged = self._build_manager_report_package(manager_id, manager_name)
        return report_pb2.HTMLResponse(html=packaged["html"])

    def GetManagerPDF(self, request, context):
        manager_id = request.manager_id
        manager_name = fetch_manager(manager_id) or f"Manager {manager_id}"
        packaged = self._build_manager_report_package(manager_id, manager_name)
        clean_temp()
        return report_pb2.PDFResponse(pdf=packaged["pdf"])

    def GetAllReportsOfManager(self, request, context):
        reports = []
        manager_id = int(request.manager_id)
        manager_name = fetch_manager(manager_id)
        mr = self._generate_manager_report_message(manager_id, manager_name)

        reports.append(mr)

        clean_temp()
        return report_pb2.AllReportsResponse(reports=reports)

    def GetAllManagerReports(self, request, context):
        all_manager_ids = fetch_all_manager_ids()
        reports = []

        if not all_manager_ids:
            print("INFO: No project owners found. Returning empty report list.")
            clean_temp()
            return report_pb2.AllReportsResponse(reports=[])

        print(f"Processing reports for {len(all_manager_ids)} managers...")

        for manager_id in all_manager_ids:
            manager_name = fetch_manager(manager_id) or f"Manager {manager_id}"
            mr = self._generate_manager_report_message(manager_id, manager_name)
            reports.append(mr)

        clean_temp()
        return report_pb2.AllReportsResponse(reports=reports)
