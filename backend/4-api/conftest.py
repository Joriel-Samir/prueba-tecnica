import secrets

import pytest

from apps.usuarios.models import Administrador, Asociado


@pytest.fixture
def password():
    """Contraseña aleatoria para cada prueba (nada escrito a mano)."""
    return secrets.token_urlsafe(16)


@pytest.fixture
def administrador(db, password):
    return Administrador.objects.create_user(
        email="admin@example.com", password=password, nombre="Ada", apellidos="Root"
    )


@pytest.fixture
def asociado(db, password):
    return Asociado.objects.create_user(
        email="ana@example.com", password=password, nombre="Ana", apellidos="Pérez"
    )
