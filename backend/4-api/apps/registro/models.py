from django.db import models


class SolicitudRegistro(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        APROBADA = 'aprobada', 'Aprobada'
        RECHAZADA = 'rechazada', 'Rechazada'

    nombre = models.CharField(max_length=200)
    email = models.EmailField()
    # Único campo extra sobre el enunciado: sin contraseña el usuario aprobado
    # no podría iniciar sesión. Se guarda ya encriptada (hash), nunca en claro.
    password = models.CharField(max_length=128)
    estado = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.PENDIENTE
    )
    fecha_solicitud = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'solicitud de registro'
        verbose_name_plural = 'solicitudes de registro'
        ordering = ['-fecha_solicitud']

    def __str__(self):
        return f'{self.email} ({self.estado})'
