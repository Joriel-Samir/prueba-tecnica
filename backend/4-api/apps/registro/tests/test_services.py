import pytest
from django.contrib.auth.hashers import make_password

from apps.registro.models import SolicitudRegistro
from apps.registro.services import (
    EmailYaRegistrado,
    SolicitudYaResuelta,
    aprobar_solicitud,
    rechazar_solicitud,
)
from apps.usuarios.models import Asociado


@pytest.fixture
def solicitud(db, password):
    return SolicitudRegistro.objects.create(
        nombre="Luis Mora", email="luis@example.com", password=make_password(password)
    )


def test_la_solicitud_nace_pendiente(solicitud):
    assert solicitud.estado == "pendiente"
    assert solicitud.fecha_solicitud is not None
    assert str(solicitud) == "luis@example.com (pendiente)"


def test_aprobar_crea_un_asociado_que_puede_iniciar_sesion(solicitud, password):
    asociado = aprobar_solicitud(solicitud)

    solicitud.refresh_from_db()
    assert solicitud.estado == "aprobada"
    assert isinstance(asociado, Asociado)
    assert asociado.email == "luis@example.com"
    assert asociado.nombre == "Luis Mora"
    assert asociado.check_password(password)


def test_aprobar_una_solicitud_ya_resuelta_falla(solicitud):
    aprobar_solicitud(solicitud)

    with pytest.raises(SolicitudYaResuelta):
        aprobar_solicitud(solicitud)


def test_aprobar_con_email_ya_registrado_falla_y_sigue_pendiente(
    solicitud, password
):
    Asociado.objects.create_user(email="LUIS@example.com", password=password)

    with pytest.raises(EmailYaRegistrado):
        aprobar_solicitud(solicitud)

    solicitud.refresh_from_db()
    assert solicitud.estado == "pendiente"


def test_rechazar_cambia_el_estado_y_no_crea_asociado(solicitud):
    rechazar_solicitud(solicitud)

    solicitud.refresh_from_db()
    assert solicitud.estado == "rechazada"
    assert Asociado.objects.count() == 0


def test_rechazar_una_solicitud_ya_resuelta_falla(solicitud):
    rechazar_solicitud(solicitud)

    with pytest.raises(SolicitudYaResuelta):
        rechazar_solicitud(solicitud)
