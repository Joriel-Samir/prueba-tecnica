from django.db.models import Q

from apps.actividades.models import Actividad
from apps.usuarios.models import Asociado


def actividades_visibles_para(usuario):
    if getattr(usuario, "es_administrador", False):
        return Actividad.objects.all()
    return Actividad.objects.filter(
        Q(asociado_id=usuario.pk) | Q(creador_id=usuario.pk)
    )


def bloquear_asociado(asociado_id):
    """Serializa escrituras por asociado en bases con soporte de locks."""
    return Asociado.objects.select_for_update().get(pk=asociado_id)


def existe_solapamiento(asociado_id, fecha_inicio, fecha_fin, excluir_id=None):
    actividades = Actividad.objects.filter(
        asociado_id=asociado_id,
        fecha_inicio__lt=fecha_fin,
        fecha_fin__gt=fecha_inicio,
    )
    if excluir_id is not None:
        actividades = actividades.exclude(pk=excluir_id)
    return actividades.exists()


def crear_actividad(**datos):
    return Actividad.objects.create(**datos)


def actualizar_actividad(actividad, datos):
    for campo, valor in datos.items():
        setattr(actividad, campo, valor)
    actividad.save()
    return actividad
