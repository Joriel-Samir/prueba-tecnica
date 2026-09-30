from datetime import timedelta
from io import BytesIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from openpyxl import Workbook
from rest_framework.test import APIClient

from apps.actividades.models import Actividad


@pytest.mark.django_db
def test_carga_csv_crea_filas_validas_y_continua_tras_solapamiento(
    administrador, asociado
):
    inicio = (timezone.now() + timedelta(days=2)).replace(microsecond=0)
    siguiente = inicio + timedelta(hours=1)
    contenido = (
        "tipo,descripcion,fecha_inicio,fecha_fin,asociado\n"
        f"Taller,Primero,{inicio.isoformat()},{siguiente.isoformat()},{asociado.email}\n"
        f"Duplicada,Solapada,{(inicio + timedelta(minutes=30)).isoformat()},"
        f"{(siguiente + timedelta(minutes=30)).isoformat()},{asociado.email}\n"
        f"Reunión,Contigua,{siguiente.isoformat()},"
        f"{(siguiente + timedelta(hours=1)).isoformat()},{asociado.email}\n"
    )
    archivo = SimpleUploadedFile(
        "actividades.csv", contenido.encode("utf-8"), content_type="text/csv"
    )
    client = APIClient()
    client.force_authenticate(administrador)

    response = client.post(
        "/api/cargamasiva/actividades/", {"file": archivo}, format="multipart"
    )

    assert response.status_code == 200
    assert response.json()["created"] == 2
    assert response.json()["errors"][0]["row"] == 3
    assert Actividad.objects.count() == 2


@pytest.mark.django_db
def test_carga_xlsx_de_actividades_es_soportada(administrador, asociado):
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["tipo", "descripcion", "fecha_inicio", "fecha_fin", "asociado"])
    inicio = (timezone.now() + timedelta(days=3)).replace(microsecond=0)
    sheet.append(
        [
            "Taller",
            "Desde Excel",
            inicio.isoformat(),
            (inicio + timedelta(hours=1)).isoformat(),
            asociado.email,
        ]
    )
    contenido = BytesIO()
    workbook.save(contenido)
    archivo = SimpleUploadedFile(
        "actividades.xlsx",
        contenido.getvalue(),
        content_type=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
    )
    client = APIClient()
    client.force_authenticate(administrador)

    response = client.post(
        "/api/cargamasiva/actividades/", {"file": archivo}, format="multipart"
    )

    assert response.status_code == 200
    assert response.json()["created"] == 1
    assert Actividad.objects.count() == 1
