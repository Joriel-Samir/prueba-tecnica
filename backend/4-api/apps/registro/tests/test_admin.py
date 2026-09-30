import pytest
from django.contrib.auth.hashers import make_password

from apps.registro.models import SolicitudRegistro
from apps.usuarios.models import Asociado

URL = "/admin/registro/solicitudregistro/"


@pytest.fixture
def solicitud(db, password):
    return SolicitudRegistro.objects.create(
        nombre="Luis Mora", email="luis@example.com", password=make_password(password)
    )


def _accion(client, nombre, solicitud):
    return client.post(URL, {"action": nombre, "_selected_action": [solicitud.pk]})


@pytest.mark.django_db
def test_administrador_aprueba_desde_el_panel(client, administrador, solicitud):
    client.force_login(administrador)

    response = _accion(client, "aprobar", solicitud)

    assert response.status_code == 302
    solicitud.refresh_from_db()
    assert solicitud.estado == "aprobada"
    assert Asociado.objects.filter(email="luis@example.com").exists()


@pytest.mark.django_db
def test_administrador_rechaza_desde_el_panel(client, administrador, solicitud):
    client.force_login(administrador)

    _accion(client, "rechazar", solicitud)

    solicitud.refresh_from_db()
    assert solicitud.estado == "rechazada"
    assert not Asociado.objects.filter(email="luis@example.com").exists()


@pytest.mark.django_db
def test_aprobar_dos_veces_no_duplica_el_asociado(client, administrador, solicitud):
    client.force_login(administrador)

    _accion(client, "aprobar", solicitud)
    _accion(client, "aprobar", solicitud)

    assert Asociado.objects.filter(email="luis@example.com").count() == 1


@pytest.mark.django_db
def test_las_solicitudes_no_se_crean_a_mano_en_el_panel(client, administrador):
    client.force_login(administrador)

    assert client.get(URL + "add/").status_code == 403


@pytest.mark.django_db
def test_asociado_no_ve_las_solicitudes(client, asociado):
    asociado.is_staff = True
    asociado.save()
    client.force_login(asociado)

    assert client.get(URL).status_code == 403
