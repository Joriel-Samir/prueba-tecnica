from django.db import transaction

from . import repositories


class ActividadSolapada(Exception):
    """La actividad propuesta se cruza con otra del mismo asociado."""


def _validar_intervalo(asociado, fecha_inicio, fecha_fin, excluir_id=None):
    if fecha_fin <= fecha_inicio:
        raise ValueError("La fecha de fin debe ser posterior a la de inicio.")
    if repositories.existe_solapamiento(
        asociado.pk, fecha_inicio, fecha_fin, excluir_id=excluir_id
    ):
        raise ActividadSolapada(
            "El asociado ya tiene una actividad en ese intervalo."
        )


@transaction.atomic
def crear_actividad(**datos):
    asociado = datos["asociado"]
    repositories.bloquear_asociado(asociado.pk)
    _validar_intervalo(asociado, datos["fecha_inicio"], datos["fecha_fin"])
    return repositories.crear_actividad(**datos)


@transaction.atomic
def actualizar_actividad(actividad, datos):
    asociado = datos.get("asociado", actividad.asociado)
    fecha_inicio = datos.get("fecha_inicio", actividad.fecha_inicio)
    fecha_fin = datos.get("fecha_fin", actividad.fecha_fin)
    repositories.bloquear_asociado(asociado.pk)
    _validar_intervalo(
        asociado, fecha_inicio, fecha_fin, excluir_id=actividad.pk
    )
    return repositories.actualizar_actividad(actividad, datos)
