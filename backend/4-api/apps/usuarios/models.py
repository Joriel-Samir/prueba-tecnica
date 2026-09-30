from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from .managers import UsuarioManager


class Usuario(AbstractBaseUser, PermissionsMixin):
    """Datos comunes de toda persona que entra al sistema (login por email).

    Administrador y Asociado son especializaciones de este modelo:
    cada uno tiene su propia tabla pero comparten estos atributos.
    """

    email = models.EmailField('correo electrónico', unique=True)
    identificacion = models.CharField(
        max_length=30, unique=True, null=True, blank=True
    )
    nombre = models.CharField(max_length=100, blank=True)
    apellidos = models.CharField(max_length=100, blank=True)
    ciudad = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField('activo', default=True)
    is_staff = models.BooleanField('acceso al panel', default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UsuarioManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f'{self.nombre} {self.apellidos}'.strip()

    def get_short_name(self):
        return self.nombre

    @property
    def es_administrador(self):
        return hasattr(self, 'administrador')

    @property
    def es_asociado(self):
        return hasattr(self, 'asociado')


class Administrador(Usuario):
    class Meta:
        verbose_name = 'administrador'
        verbose_name_plural = 'administradores'

    def save(self, *args, **kwargs):
        self.is_staff = True  # los administradores siempre entran al panel
        super().save(*args, **kwargs)


class Asociado(Usuario):
    class Meta:
        verbose_name = 'asociado'
        verbose_name_plural = 'asociados'
