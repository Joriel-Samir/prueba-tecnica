from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from apps.actividades.models import Actividad
from apps.usuarios.models import Asociado

URL = "/api/actividades/"


def _payload(asociado, inicio=None, fin=None, **extra):
    inicio = inicio or timezone.now().replace(microsecond=0)
    datos = {
        "tipo": "Reunión",
        "descripcion": "Seguimiento",
        "fecha_inicio": inicio.isoformat(),
        "fecha_fin": (fin or inicio + timedelta(hours=1)).isoformat(),
        "asociado": asociado.pk,
    }
    datos.update(extra)
    return datos


def _crear_actividad(asociado, creador, inicio=None, fin=None, **extra):
    inicio = inicio or timezone.now().replace(microsecond=0)
    return Actividad.objects.create(
        tipo="Reunión",
        fecha_inicio=inicio,
        fecha_fin=fin or inicio + timedelta(hours=1),
        asociado=asociado,
        creador=creador,
        **extra,
    )


@pytest.mark.django_db
def test_api_requiere_autenticacion():
    assert APIClient().get(URL).status_code == 401


@pytest.mark.django_db
def test_administrador_crea_actualiza_y_elimina_actividad(administrador, asociado):
    client = APIClient()
    client.force_authenticate(administrador)

    response = client.post(URL, _payload(asociado), format="json")

    assert response.status_code == 201
    assert response.json()["creador"] == administrador.pk
    actividad_id = response.json()["id"]
    assert client.patch(
        f"{URL}{actividad_id}/", {"tipo": "Taller"}, format="json"
    ).status_code == 200
    assert client.delete(f"{URL}{actividad_id}/").status_code == 204
    assert not Actividad.objects.filter(pk=actividad_id).exists()


@pytest.mark.django_db
def test_asociado_puede_crear_solo_actividades_para_si(asociado):
    otro = Asociado.objects.create_user(
        email="otro@example.com", password="otra-password", nombre="Otro"
    )
    client = APIClient()
    client.force_authenticate(asociado)

    propia = client.post(URL, _payload(asociado), format="json")
    ajena = client.post(URL, _payload(otro), format="json")

    assert propia.status_code == 201
    assert propia.json()["creador"] == asociado.pk
    assert ajena.status_code == 403
    assert Actividad.objects.count() == 1


@pytest.mark.django_db
def test_asociado_ve_solo_actividades_asignadas_o_creadas(asociado, administrador):
    otra = Asociado.objects.create_user(
        email="otro@example.com", password="otra-password", nombre="Otro"
    )
    asignada = _crear_actividad(asociado, administrador)
    creada = _crear_actividad(otra, asociado)
    _crear_actividad(otra, administrador)
    client = APIClient()
    client.force_authenticate(asociado)

    response = client.get(URL)

    assert response.status_code == 200
    assert {item["id"] for item in response.json()} == {asignada.pk, creada.pk}


@pytest.mark.django_db
def test_asociado_no_puede_editar_actividad_asignada(asociado, administrador):
    actividad = _crear_actividad(asociado, administrador)
    client = APIClient()
    client.force_authenticate(asociado)

    response = client.patch(
        f"{URL}{actividad.pk}/", {"tipo": "Cambio"}, format="json"
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_creador_puede_editar_actividad_creada(asociado):
    otro = Asociado.objects.create_user(
        email="otro@example.com", password="otra-password", nombre="Otro"
    )
    actividad = _crear_actividad(otro, asociado)
    client = APIClient()
    client.force_authenticate(asociado)

    response = client.patch(
        f"{URL}{actividad.pk}/", {"tipo": "Cambio"}, format="json"
    )

    assert response.status_code == 200
    assert response.json()["tipo"] == "Cambio"


@pytest.mark.django_db
def test_no_permite_solapar_actividades_del_mismo_asociado(
    administrador, asociado
):
    inicio = timezone.now().replace(microsecond=0)
    _crear_actividad(asociado, administrador, inicio)
    client = APIClient()
    client.force_authenticate(administrador)

    response = client.post(
        URL,
        _payload(asociado, inicio + timedelta(minutes=30)),
        format="json",
    )

    assert response.status_code == 400
    assert Actividad.objects.count() == 1


@pytest.mark.django_db
def test_permite_actividades_contiguas_sin_solapamiento(administrador, asociado):
    inicio = timezone.now().replace(microsecond=0)
    _crear_actividad(asociado, administrador, inicio)
    client = APIClient()
    client.force_authenticate(administrador)

    response = client.post(
        URL,
        _payload(asociado, inicio + timedelta(hours=1)),
        format="json",
    )

    assert response.status_code == 201


@pytest.mark.django_db
def test_filtro_desde_y_hasta_incluye_los_limites(administrador, asociado):
    primer_dia = timezone.now().replace(hour=9, minute=0, second=0, microsecond=0)
    dentro = _crear_actividad(asociado, administrador, primer_dia)
    fuera = _crear_actividad(asociado, administrador, primer_dia + timedelta(days=2))
    client = APIClient()
    client.force_authenticate(administrador)

    response = client.get(
        URL,
        {
            "desde": primer_dia.date().isoformat(),
            "hasta": (primer_dia + timedelta(days=1)).date().isoformat(),
        },
    )

    assert response.status_code == 200
    assert {item["id"] for item in response.json()} == {dentro.pk}
    assert fuera.pk not in {item["id"] for item in response.json()}


@pytest.mark.django_db
def test_filtro_fechas_invalido_devuelve_400(administrador):
    client = APIClient()
    client.force_authenticate(administrador)

    response = client.get(URL, {"desde": "ayer"})

    assert response.status_code == 400
