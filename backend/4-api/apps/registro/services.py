from django.contrib.auth.hashers import make_password
from django.db import transaction

from . import repositories
from .models import SolicitudRegistro


class SolicitudError(Exception):
    """Error de negocio al resolver una solicitud."""


class SolicitudYaResuelta(SolicitudError):
    pass


class EmailYaRegistrado(SolicitudError):
    pass


class SolicitudPendienteExistente(SolicitudError):
    pass


@transaction.atomic
def crear_solicitud_registro(nombre, email, password):
    """Registra una solicitud pendiente sin persistir la contraseña en claro."""
    if repositories.email_ya_registrado(email):
        raise EmailYaRegistrado('Ya existe un usuario con ese correo.')
    if repositories.solicitud_pendiente_para_email(email):
        raise SolicitudPendienteExistente(
            'Ya existe una solicitud pendiente para ese correo.'
        )
    return repositories.crear_solicitud(
        nombre=nombre,
        email=email,
        password_hash=make_password(password),
    )


def _validar_pendiente(solicitud):
    if solicitud.estado != SolicitudRegistro.Estado.PENDIENTE:
        raise SolicitudYaResuelta('La solicitud ya fue resuelta.')


@transaction.atomic
def aprobar_solicitud(solicitud):
    """Crea el Asociado con los datos de la solicitud y la marca aprobada."""
    _validar_pendiente(solicitud)
    if repositories.email_ya_registrado(solicitud.email):
        raise EmailYaRegistrado('Ya existe un usuario con ese correo.')

    asociado = repositories.crear_asociado(
        email=solicitud.email,
        nombre=solicitud.nombre,
        password_hash=solicitud.password,
    )
    solicitud.estado = SolicitudRegistro.Estado.APROBADA
    solicitud.save(update_fields=['estado'])
    return asociado


def rechazar_solicitud(solicitud):
    _validar_pendiente(solicitud)
    solicitud.estado = SolicitudRegistro.Estado.RECHAZADA
    solicitud.save(update_fields=['estado'])
