import os
from urllib.parse import urlparse
import requests
from openpyxl import load_workbook, Workbook
from docx import Document
from doc2docx import convert

from constants import DOWNLOADED_SCHEDULES_DIR


def download_file(url: str, filename: str) -> None:
    """Download a file from the given URL and save it to the given filename."""
    response = requests.get(url, verify=False)  # Handle SSL warnings properly
    with open(filename, 'wb') as file:
        file.write(response.content)


def load_excel_file(filename: str) -> Workbook:
    """Load an Excel file from the given filename."""
    return load_workbook(filename)


def convert_doc_to_docx(filename: str) -> str:
    """Convert a Word file to the Word 2007+ format."""
    docx_path = os.path.splitext(filename)[0] + '.docx'
    if not os.path.exists(docx_path):
        convert(filename, docx_path)
    return docx_path


def load_doc_file(filename: str) -> Workbook:
    """Load a Word file from the given filename."""
    docx_path = convert_doc_to_docx(filename)
    doc = Document(docx_path)

    wb = Workbook()
    ws = wb.active

    for i, para in enumerate(doc.paragraphs):
        cells = [sentence.strip() for sentence in para.text.split('.') if sentence]

        for j, cell in enumerate(cells):
            ws.cell(row=i + 1, column=j + 1, value=cell)

    row_offset = len(doc.paragraphs)

    for table in doc.tables:
        for i, row in enumerate(table.rows):
            for j, cell in enumerate(row.cells):
                ws.cell(row=row_offset + i + 1, column=j + 1, value=cell.text)

    return wb


def load_workbook_from_file(url: str):
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)
    file_extension = os.path.splitext(filename)[-1].lower()

    if not os.path.exists(DOWNLOADED_SCHEDULES_DIR):
        os.makedirs(DOWNLOADED_SCHEDULES_DIR)

    local_path = os.path.join(DOWNLOADED_SCHEDULES_DIR, filename)
    if not os.path.exists(local_path):
        download_file(url, local_path)

    if file_extension == '.xlsx':
        return load_excel_file(local_path)

    if file_extension == '.doc' or file_extension == '.docx':
        return load_doc_file(local_path)

    raise ValueError(f'Unknown file extension: {file_extension}')
