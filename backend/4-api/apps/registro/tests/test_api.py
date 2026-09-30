import pytest
from django.contrib.auth.hashers import check_password
from rest_framework.test import APIClient

from apps.registro.models import SolicitudRegistro


@pytest.mark.django_db
def test_registro_publico_crea_solicitud_y_no_expone_password(password):
    response = APIClient().post(
        "/api/registro/",
        {
            "nombre": "Luis Mora",
            "email": "luis@example.com",
            "password": password,
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.json()["estado"] == SolicitudRegistro.Estado.PENDIENTE
    assert "password" not in response.json()
    solicitud = SolicitudRegistro.objects.get(email="luis@example.com")
    assert check_password(password, solicitud.password)


@pytest.mark.django_db
def test_registro_rechaza_datos_invalidos():
    response = APIClient().post(
        "/api/registro/",
        {"nombre": "Luis", "email": "no-es-email", "password": "corta"},
        format="json",
    )

    assert response.status_code == 400
    assert not SolicitudRegistro.objects.exists()


@pytest.mark.django_db
def test_registro_rechaza_email_con_solicitud_pendiente(password):
    client = APIClient()
    datos = {
        "nombre": "Luis Mora",
        "email": "luis@example.com",
        "password": password,
    }
    assert client.post("/api/registro/", datos, format="json").status_code == 201

    response = client.post(
        "/api/registro/",
        {**datos, "email": "LUIS@example.com"},
        format="json",
    )

    assert response.status_code == 409
    assert SolicitudRegistro.objects.count() == 1


@pytest.mark.django_db
def test_registro_rechaza_email_ya_registrado(asociado, password):
    response = APIClient().post(
        "/api/registro/",
        {
            "nombre": "Ana",
            "email": asociado.email,
            "password": password,
        },
        format="json",
    )

    assert response.status_code == 409
    assert not SolicitudRegistro.objects.exists()


@pytest.mark.django_db
def test_registro_no_permite_consultar_solicitudes():
    response = APIClient().get("/api/registro/")

    assert response.status_code == 405
