from io import BytesIO

import pytest
from django.contrib.auth.hashers import check_password
from django.core.files.uploadedfile import SimpleUploadedFile
from openpyxl import Workbook
from rest_framework.test import APIClient

from apps.usuarios.models import Asociado

URL = "/api/asociados/"


@pytest.mark.django_db
def test_admin_lista_asociados(administrador, asociado):
    client = APIClient()
    client.force_authenticate(administrador)

    response = client.get(URL)

    assert response.status_code == 200
    assert [row["email"] for row in response.json()] == [asociado.email]


@pytest.mark.django_db
def test_admin_crea_asociado_con_password_hasheado(administrador, password):
    client = APIClient()
    client.force_authenticate(administrador)

    response = client.post(
        URL,
        {
            "email": "nuevo@example.com",
            "password": password,
            "identificacion": "A-100",
            "nombre": "Nuevo",
            "apellidos": "Asociado",
            "ciudad": "Cali",
        },
        format="json",
    )

    assert response.status_code == 201
    assert "password" not in response.json()
    creado = Asociado.objects.get(email="nuevo@example.com")
    assert check_password(password, creado.password)


@pytest.mark.django_db
def test_asociado_no_administra_asociados(asociado):
    client = APIClient()
    client.force_authenticate(asociado)

    response = client.get(URL)

    assert response.status_code == 403
    assert "error" in response.json()


@pytest.mark.django_db
def test_crear_asociado_duplicado_devuelve_409(administrador, asociado, password):
    client = APIClient()
    client.force_authenticate(administrador)

    response = client.post(
        URL,
        {"email": asociado.email, "password": password, "nombre": "Duplicado"},
        format="json",
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "conflict"


@pytest.mark.django_db
def test_carga_csv_crea_filas_validas_y_reporta_invalidas(administrador):
    client = APIClient()
    client.force_authenticate(administrador)
    contenido = (
        "email,password,identificacion,nombre,apellidos,ciudad\n"
        "ana@example.com,secure-password,A-1,Ana,Luz,Cali\n"
        "mal-correo,secure-password,A-2,Mal,Correo,Bogota\n"
    )
    archivo = SimpleUploadedFile(
        "asociados.csv", contenido.encode("utf-8"), content_type="text/csv"
    )

    response = client.post(
        "/api/carga-masiva/asociados/", {"file": archivo}, format="multipart"
    )

    assert response.status_code == 200
    assert response.json()["created"] == 1
    assert response.json()["errors"][0]["row"] == 3
    assert "email" in response.json()["errors"][0]["details"]
    assert Asociado.objects.filter(email="ana@example.com").exists()


@pytest.mark.django_db
def test_carga_xlsx_crea_filas_validas_y_reporta_invalidas(
    administrador, password
):
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(
        ["email", "password", "identificacion", "nombre", "apellidos", "ciudad"]
    )
    sheet.append(
        ["ana@example.com", password, "A-10", "Ana", "Luz", "Cali"]
    )
    sheet.append(
        ["email-invalido", password, "A-11", "Eva", "Ríos", "Pasto"]
    )
    contenido = BytesIO()
    workbook.save(contenido)
    archivo = SimpleUploadedFile("asociados.xlsx", contenido.getvalue())
    client = APIClient()
    client.force_authenticate(administrador)

    response = client.post(
        "/api/carga-masiva/asociados/", {"file": archivo}, format="multipart"
    )

    assert response.status_code == 200
    assert response.json()["created"] == 1
    assert response.json()["total"] == 2
    assert response.json()["errors"][0]["row"] == 3
    assert "email" in response.json()["errors"][0]["details"]
    creado = Asociado.objects.get(email="ana@example.com")
    assert check_password(password, creado.password)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "filename, content",
    [
        ("documento.docx", b"word document is not a supported import format"),
        ("archivo.xlsx", b"not-a-valid-xlsx-zip"),
    ],
)
def test_carga_masiva_rechaza_word_y_xlsx_danado_con_error_uniforme(
    administrador, filename, content
):
    client = APIClient()
    client.force_authenticate(administrador)
    archivo = SimpleUploadedFile(filename, content)

    response = client.post(
        "/api/carga-masiva/asociados/", {"file": archivo}, format="multipart"
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_request"
    assert response.json()["error"]["details"]
    assert not Asociado.objects.exists()
