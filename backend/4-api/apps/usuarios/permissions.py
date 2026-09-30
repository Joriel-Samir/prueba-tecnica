from rest_framework.permissions import BasePermission


class IsAdministrador(BasePermission):
    message = "Only administrators may manage associates."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "es_administrador", False)
        )
