from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class ReportDTO:
    manager_id: int
    manager_name: str
    html: str
    pdf_path: Optional[str]
    charts: Dict[str, str]
    file_name: str