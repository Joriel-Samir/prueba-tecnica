from apps.usuarios.models import Asociado, Usuario


def listar_asociados():
    return Asociado.objects.order_by("email")


def email_ya_registrado(email):
    return Usuario.objects.filter(email__iexact=email).exists()


def identificacion_ya_registrada(identificacion):
    return bool(
        identificacion
        and Usuario.objects.filter(identificacion__iexact=identificacion).exists()
    )


def crear_asociado(**datos):
    password = datos.pop("password")
    return Asociado.objects.create_user(password=password, **datos)
