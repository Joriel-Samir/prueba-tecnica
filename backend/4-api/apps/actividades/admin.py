from django.contrib import admin

from apps.core.admin_mixins import SoloAdministradores

from .models import Actividad


@admin.register(Actividad)
class ActividadAdmin(SoloAdministradores, admin.ModelAdmin):
    list_display = ('tipo', 'asociado', 'fecha_inicio', 'fecha_fin', 'creador')
    list_filter = ('tipo',)
    search_fields = ('tipo', 'descripcion', 'asociado__email')
    date_hierarchy = 'fecha_inicio'
