from datetime import timedelta

import pytest
from django.db import IntegrityError
from django.utils import timezone

from apps.actividades.models import Actividad


def _datos(asociado, administrador, **extra):
    inicio = timezone.now()
    datos = {
        "tipo": "Reunión",
        "fecha_inicio": inicio,
        "fecha_fin": inicio + timedelta(hours=1),
        "asociado": asociado,
        "creador": administrador,
    }
    datos.update(extra)
    return datos


def test_crear_actividad(asociado, administrador):
    actividad = Actividad.objects.create(**_datos(asociado, administrador))

    assert actividad.descripcion == ""
    assert actividad.asociado == asociado
    assert actividad.creador == administrador
    assert "Reunión" in str(actividad)


def test_la_fecha_fin_debe_ser_posterior_al_inicio(asociado, administrador):
    inicio = timezone.now()

    with pytest.raises(IntegrityError):
        Actividad.objects.create(
            **_datos(asociado, administrador, fecha_inicio=inicio, fecha_fin=inicio)
        )


def test_borrar_el_asociado_borra_sus_actividades(asociado, administrador):
    Actividad.objects.create(**_datos(asociado, administrador))

    asociado.delete()

    assert Actividad.objects.count() == 0
