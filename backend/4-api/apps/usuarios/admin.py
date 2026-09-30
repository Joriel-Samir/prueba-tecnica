from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from apps.core.admin_mixins import SoloAdministradores

from .models import Administrador, Asociado, Usuario


class PersonaCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ('email',)
        field_classes = {}


class PersonaChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = Usuario
        fields = '__all__'


class PersonaAdmin(SoloAdministradores, UserAdmin):
    """Admin común para Administrador y Asociado."""

    form = PersonaChangeForm
    add_form = PersonaCreationForm

    list_display = ('email', 'nombre', 'apellidos', 'identificacion', 'ciudad')
    list_filter = ('is_active', 'ciudad')
    search_fields = ('email', 'nombre', 'apellidos', 'identificacion')
    ordering = ('email',)
    filter_horizontal = ()

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            'Datos personales',
            {'fields': ('identificacion', 'nombre', 'apellidos', 'ciudad')},
        ),
        ('Estado', {'fields': ('is_active',)}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'email',
                    'password1',
                    'password2',
                    'identificacion',
                    'nombre',
                    'apellidos',
                    'ciudad',
                ),
            },
        ),
    )


admin.site.register(Administrador, PersonaAdmin)
admin.site.register(Asociado, PersonaAdmin)
