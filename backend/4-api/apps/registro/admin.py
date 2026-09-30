from django.contrib import admin, messages

from apps.core.admin_mixins import SoloAdministradores

from .models import SolicitudRegistro
from .services import SolicitudError, aprobar_solicitud, rechazar_solicitud


@admin.register(SolicitudRegistro)
class SolicitudRegistroAdmin(SoloAdministradores, admin.ModelAdmin):
    list_display = ('nombre', 'email', 'estado', 'fecha_solicitud')
    list_filter = ('estado',)
    search_fields = ('nombre', 'email')
    # El estado solo cambia con las acciones (que pasan por el servicio)
    readonly_fields = ('nombre', 'email', 'password', 'estado', 'fecha_solicitud')
    actions = ['aprobar', 'rechazar']

    def has_add_permission(self, request):
        return False  # las solicitudes llegan por la API pública

    @admin.action(description='Aprobar solicitudes seleccionadas')
    def aprobar(self, request, queryset):
        self._resolver(request, queryset, aprobar_solicitud, 'aprobada(s)')

    @admin.action(description='Rechazar solicitudes seleccionadas')
    def rechazar(self, request, queryset):
        self._resolver(request, queryset, rechazar_solicitud, 'rechazada(s)')

    def _resolver(self, request, queryset, accion, texto):
        resueltas = 0
        for solicitud in queryset:
            try:
                accion(solicitud)
                resueltas += 1
            except SolicitudError as error:
                self.message_user(
                    request, f'{solicitud.email}: {error}', level=messages.WARNING
                )
        self.message_user(request, f'{resueltas} solicitud(es) {texto}.')
