from io import BytesIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from openpyxl import Workbook

from apps.core.uploads import parse_tabular_upload


def test_parsea_csv_con_bom_y_normaliza_encabezados():
    upload = SimpleUploadedFile(
        "datos.csv", "\ufeffNombre,Email\nAna,ana@example.com\n".encode("utf-8")
    )

    rows = parse_tabular_upload(upload)

    assert rows == [(2, {"nombre": "Ana", "email": "ana@example.com"})]


def test_parsea_hoja_xlsx():
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["Nombre", "Email"])
    sheet.append(["Ana", "ana@example.com"])
    buffer = BytesIO()
    workbook.save(buffer)
    upload = SimpleUploadedFile("datos.xlsx", buffer.getvalue())

    assert parse_tabular_upload(upload) == [
        (2, {"nombre": "Ana", "email": "ana@example.com"})
    ]


def test_rechaza_extension_no_soportada():
    upload = SimpleUploadedFile("datos.xls", b"contenido")

    with pytest.raises(ValueError, match=".csv or .xlsx"):
        parse_tabular_upload(upload)
