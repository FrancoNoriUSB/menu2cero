# -*- encoding: utf-8 -*-
from django.contrib import admin
from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from models import *
from forms import *

class UserAdmin(UserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'password', 'nombre')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informacion Personal', {'fields': ('email', 'nombre')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nombre', 'password1', 'password2')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    list_filter = ('email',)
    filter_horizontal = ()

# Now register the new UserAdmin...
admin.site.register(User, UserAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)

#Clase para agregar al admin la tabla de rest
class RestauranteAdmin(admin.TabularInline):
	model = Restaurante
	extra = 0

admin.site.register(Categoria)
admin.site.register(Ciudad)
admin.site.register(Cliente)
admin.site.register(Comensal)
admin.site.register(Direccion)
admin.site.register(Horario)
admin.site.register(Imagen)
admin.site.register(Menu)
admin.site.register(Metodo)
admin.site.register(Plan)
admin.site.register(Plato)
admin.site.register(Pago)
admin.site.register(Red_social)
admin.site.register(Restaurante)
admin.site.register(Servicio)
admin.site.register(TelefonoRestaurante)
admin.site.register(Voto)
admin.site.register(Zona)