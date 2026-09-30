import csv
from io import StringIO
from pathlib import Path
from zipfile import BadZipFile

from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException


def parse_tabular_upload(upload):
    """Returns (physical row number, normalized row) pairs for CSV or XLSX."""
    extension = Path(upload.name).suffix.lower()
    if extension == ".csv":
        try:
            text = upload.read().decode("utf-8-sig")
        except UnicodeDecodeError as error:
            raise ValueError("CSV files must use UTF-8 encoding.") from error
        reader = csv.DictReader(StringIO(text))
        if not reader.fieldnames:
            raise ValueError("The file must include a header row.")
        return [
            (row_number, _normalize_row(row))
            for row_number, row in enumerate(reader, start=2)
            if any(value not in (None, "") for value in row.values())
        ]
    if extension == ".xlsx":
        try:
            workbook = load_workbook(upload, read_only=True, data_only=True)
        except (BadZipFile, InvalidFileException, KeyError) as error:
            raise ValueError("The uploaded XLSX file is invalid.") from error
        sheet = workbook.active
        values = sheet.iter_rows(values_only=True)
        headers = next(values, None)
        if not headers or not any(header is not None for header in headers):
            raise ValueError("The file must include a header row.")
        normalized_headers = [_normalize_header(header) for header in headers]
        rows = []
        for row_number, values_row in enumerate(values, start=2):
            row = dict(zip(normalized_headers, values_row, strict=False))
            if any(value not in (None, "") for value in row.values()):
                rows.append((row_number, row))
        workbook.close()
        return rows
    raise ValueError("Upload a .csv or .xlsx file.")


def _normalize_header(value):
    return str(value).strip().lower().replace(" ", "_") if value else ""


def _normalize_row(row):
    return {
        _normalize_header(key): value
        for key, value in row.items()
        if key is not None
    }
