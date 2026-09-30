from rest_framework.permissions import SAFE_METHODS, BasePermission


class ActividadPermission(BasePermission):
    """Acceso total para administradores y limitado para asociados."""

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return getattr(user, "es_administrador", False) or getattr(
            user, "es_asociado", False
        )

    def has_object_permission(self, request, view, obj):
        user = request.user
        if getattr(user, "es_administrador", False):
            return True
        if request.method in SAFE_METHODS:
            return obj.creador_id == user.pk or obj.asociado_id == user.pk
        return obj.creador_id == user.pk
