from apps.registro.models import SolicitudRegistro
from apps.usuarios.models import Asociado, Usuario


def email_ya_registrado(email):
    return Usuario.objects.filter(email__iexact=email).exists()


def solicitud_pendiente_para_email(email):
    return SolicitudRegistro.objects.filter(
        email__iexact=email, estado=SolicitudRegistro.Estado.PENDIENTE
    ).exists()


def crear_solicitud(nombre, email, password_hash):
    return SolicitudRegistro.objects.create(
        nombre=nombre,
        email=Usuario.objects.normalize_email(email),
        password=password_hash,
    )


def crear_asociado(email, nombre, password_hash):
    asociado = Asociado(
        email=Usuario.objects.normalize_email(email),
        nombre=nombre,
        password=password_hash,  # ya viene encriptada desde la solicitud
    )
    asociado.save()
    return asociado
