import os
from datetime import datetime
from venv import logger

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.openapi.models import Response
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from config.settings import settings
from reports.report_generator import generate_manager_report
from server.service_impl import ReportServiceServicer
from server.generated import report_pb2

router = APIRouter()

report_service = ReportServiceServicer()

security = HTTPBearer()

def validate_token(token: str) -> bool:
    # Example: Check against a simple static secret key
    SECRET_KEY = settings.api_key
    return token == SECRET_KEY

def clean_temp():
    try:
        for item_name in os.listdir(settings.pdf_path):
            os.remove(os.path.join(settings.pdf_path, item_name))
        print(f"Cleaned up temporary files: {settings.pdf_path}")
    except OSError as e:
        print(f"Error: Failed to delete temporary file {settings.pdf_path}. Error: {e}")

class ReportDownload(BaseModel):
    pdf_base64: str
    html_content: str

@router.get("/reports/manager/{manager_id}/pdf", response_class=FileResponse)
async def get_manager_pdf(manager_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Retrieves PDF report bytes (Base64) for a single manager."""
    if not validate_token(credentials.credentials):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired API Key/Token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        generate_manager_report(manager_id)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"/manager_{manager_id}_{timestamp}.pdf"
        pdf_path = settings.pdf_path + file_name

        return FileResponse(pdf_path, filename=file_name, media_type='application/pdf')

    except Exception as e:
        # Handle exceptions gracefully
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports/manager/{manager_id}/html", response_class=HTMLResponse)
async def get_manager_html(manager_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Retrieves HTML report content for a single manager."""
    if not validate_token(credentials.credentials):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired API Key/Token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        manager_request = report_pb2.ManagerRequest(manager_id=manager_id)
        response = report_service.GetAllReportsOfManager(manager_request, None)

        if not response.reports or not response.reports[0].html:
            raise HTTPException(status_code=404, detail="Report not found or empty.")

        return response.reports[0].html # Directly return the HTML string

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))