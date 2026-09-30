from django.conf import settings
from django.db import models
from django.db.models import F, Q


class Actividad(models.Model):
    tipo = models.CharField('tipo de actividad', max_length=100)
    descripcion = models.TextField(blank=True)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    asociado = models.ForeignKey(
        'usuarios.Asociado',
        on_delete=models.CASCADE,
        related_name='actividades',
    )
    creador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='actividades_creadas',
    )

    class Meta:
        verbose_name = 'actividad'
        verbose_name_plural = 'actividades'
        ordering = ['fecha_inicio']
        indexes = [models.Index(fields=['asociado', 'fecha_inicio'])]
        constraints = [
            models.CheckConstraint(
                condition=Q(fecha_fin__gt=F('fecha_inicio')),
                name='actividad_fin_posterior_a_inicio',
            )
        ]

    def __str__(self):
        return f'{self.tipo} ({self.fecha_inicio:%Y-%m-%d %H:%M})'
