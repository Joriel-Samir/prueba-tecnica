class SoloAdministradores:
    """Mixin para el admin de Django: solo los usuarios con rol Administrador
    ven y modifican el modelo (no basta con tener is_staff)."""

    def _es_administrador(self, request):
        return request.user.is_authenticated and request.user.es_administrador

    def has_module_permission(self, request):
        return self._es_administrador(request)

    def has_view_permission(self, request, obj=None):
        return self._es_administrador(request)

    def has_add_permission(self, request):
        return self._es_administrador(request)

    def has_change_permission(self, request, obj=None):
        return self._es_administrador(request)

    def has_delete_permission(self, request, obj=None):
        return self._es_administrador(request)
