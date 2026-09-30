import pytest
from django.contrib.auth.hashers import check_password
from django.core.files.uploadedfile import SimpleUploadedFile
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
