# -*- coding: utf-8 -*-
from django import forms
from models import *
from django.contrib import admin
from django.forms.extras.widgets import *
from django.contrib.auth.models import Group
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.admin import UserAdmin

# Define el formulario para la creacion de los usuarios
class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'nombre')
 
    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


# Formulario para cambiar el usuario
class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'password', 'nombre')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


#Formulario de datos de cliente
class ClienteForm(forms.ModelForm):

	class Meta:
		model = Cliente
		fields = ('cargo','telefono')
		widgets = {
			'cargo': forms.Select(attrs={'placeholder':'Cargo'}),
			'telefono': forms.TextInput(attrs={'placeholder':'Teléfono'}),
		}
		labels = {
			'telefono': 'Teléfono',
		}


#Formulario de modificacion de contrasena
class modificarContrasenaForm(PasswordChangeForm):

	class Meta(PasswordChangeForm):
		labels = {
		
		}


#Formulario de busqueda del header
class BuscadorForm(forms.Form):
	palabra = forms.CharField(widget=forms.TextInput(attrs={'placeholder':"restaurante, categoría, plato, lugar, etc",'class':"form-control"}), required=True)


#Formulario de filtro de categorias y restaurantes
class FiltroForm(forms.Form):

	choices_tipo = (('','- Tipo -'), 
		('Restaurante', 'Restaurante'),
		('Bar', 'Bar'),
		(u'Heladería', u'Heladería'),
		('Panadería', u'Panadería'),
		(u'café', 'Cafetería'),)
	choices_servicios = (
		('Wifi', 'Wifi'), 
		('Exterior', 'Exterior'), 
		('Estacionamiento', 'Estacionamiento'), 
		('Delivery', 'Delivery'), 
		('Reservacion','Reservar'), 
		('Musica', 'Musica en vivo'), 
		('Local_Nocturno', 'Sitio Nocturno'), )

	Categorias = forms.ModelChoiceField(queryset=Categoria.objects.all().values_list('nombre', flat=True).distinct().order_by('nombre'), empty_label='- Categorías -', required=False, to_field_name="nombre")

	Ciudad = forms.ModelChoiceField(queryset=Ciudad.objects.all().values_list('nombre', flat=True).distinct().order_by('nombre'), empty_label='- Ciudad -', required=False, to_field_name="nombre")

	Zona = forms.ModelChoiceField(queryset=Zona.objects.all().values_list('nombre', flat=True).distinct().order_by('nombre'), empty_label='- Zona -', required=False, to_field_name="nombre")

	Tipo = forms.ChoiceField(choices=choices_tipo, required=False)

	Servicios = forms.MultipleChoiceField(choices=choices_servicios, widget=forms.CheckboxSelectMultiple, required=False)


#Formulario de contactanos
class ContactForm(forms.Form):

	nombre = forms.CharField(widget=forms.TextInput(attrs={'placeholder':"Nombre",'class':"form-control"}), required=True)
	correo = forms.CharField(widget=forms.EmailInput(attrs={'placeholder':"Correo",'class':"form-control"}), required=True)
	telefono = forms.CharField(widget=forms.TextInput(attrs={'placeholder':"Teléfono",'class':"form-control"}), required=True)
	mensaje = forms.CharField(widget=forms.Textarea(attrs={'placeholder':"Mensaje",'class':"form-control"}), required=True)
