import sys

from weasyprint import HTML
from pathlib import Path

def generate_pdf_from_html(html_content: str, output_path: str):
    output_path = Path(output_path)
    project_root = Path(sys.argv[0]).resolve().parent
    current_base_url = project_root.as_uri()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    HTML(
        string=html_content,
        base_url=current_base_url
    ).write_pdf(output_path)