from django.contrib.auth.base_user import BaseUserManager


class UsuarioManager(BaseUserManager):
    """Manager para un usuario que se identifica por email (sin username)."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El correo es obligatorio')
        email = self.normalize_email(email)
        usuario = self.model(email=email, **extra_fields)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, email, password=None, **extra_fields):
        """Lo usa `createsuperuser`: el superusuario es un Administrador."""
        from .models import Administrador  # import aquí para evitar ciclo

        extra_fields.setdefault('is_superuser', True)
        administrador = Administrador(
            email=self.normalize_email(email), **extra_fields
        )
        administrador.set_password(password)
        administrador.save(using=self._db)
        return administrador
