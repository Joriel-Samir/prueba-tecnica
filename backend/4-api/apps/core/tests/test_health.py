import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_health_ok():
    response = APIClient().get("/api/health/")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


def test_health_devuelve_503_si_la_base_de_datos_falla(monkeypatch):
    monkeypatch.setattr("apps.core.views.check_database", lambda: False)

    response = APIClient().get("/api/health/")

    assert response.status_code == 503
    assert response.json() == {"status": "error", "database": "error"}


@pytest.mark.django_db
def test_check_database_devuelve_false_si_la_consulta_falla(monkeypatch):
    from django.db import DatabaseError

    from apps.core.services import check_database

    def cursor_roto():
        raise DatabaseError("sin conexión")

    monkeypatch.setattr("apps.core.services.connection.cursor", cursor_roto)

    assert check_database() is False
