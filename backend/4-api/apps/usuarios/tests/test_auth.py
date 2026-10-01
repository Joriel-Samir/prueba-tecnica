import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
@pytest.mark.parametrize("fixture,role", [("asociado", "associate"), ("administrador", "admin")])
def test_login_con_email_devuelve_access_y_refresh(fixture, role, password, request):
    usuario = request.getfixturevalue(fixture)

    response = APIClient().post(
        "/api/auth/token/", {"email": usuario.email, "password": password}
    )

    assert response.status_code == 200
    assert "access" in response.json()
    assert "refresh" in response.json()
    assert response.json()["role"] == role


@pytest.mark.django_db
def test_login_con_password_incorrecta_devuelve_401(asociado):
    response = APIClient().post(
        "/api/auth/token/", {"email": asociado.email, "password": "incorrecta"}
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_refresh_devuelve_un_nuevo_access(asociado, password):
    client = APIClient()
    tokens = client.post(
        "/api/auth/token/", {"email": asociado.email, "password": password}
    ).json()

    response = client.post("/api/auth/token/refresh/", {"refresh": tokens["refresh"]})

    assert response.status_code == 200
    assert "access" in response.json()


@pytest.mark.django_db
def test_refresh_con_token_invalido_devuelve_401():
    response = APIClient().post("/api/auth/token/refresh/", {"refresh": "no-es-token"})

    assert response.status_code == 401
