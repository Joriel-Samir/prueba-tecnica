import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_openapi_schema_and_swagger_are_expuestos():
    client = APIClient()

    schema = client.get("/api/schema/")
    docs = client.get("/api/docs/")

    assert schema.status_code == 200
    assert "/api/asociados/" in schema.content.decode()
    assert "/api/carga-masiva/asociados/" in schema.content.decode()
    assert "/api/cargamasiva/actividades/" in schema.content.decode()
    assert docs.status_code == 200


@pytest.mark.django_db
def test_error_401_usa_formato_uniforme():
    response = APIClient().get("/api/actividades/")

    assert response.status_code == 401
    assert set(response.json()) == {"error"}
    assert set(response.json()["error"]) == {"code", "message", "details"}


@pytest.mark.django_db
def test_error_404_usa_formato_uniforme(administrador):
    client = APIClient()
    client.force_authenticate(administrador)

    response = client.get("/api/actividades/999999/")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"
