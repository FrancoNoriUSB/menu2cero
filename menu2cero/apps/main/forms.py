# -*- coding: utf-8 -*-
from django.forms import ModelForm, Textarea
from django import forms
from models import *
from django.forms.extras.widgets import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm

#Formulario de registro simple de usuario
class UserForm(ModelForm):
	confirm_password = forms.CharField(widget=forms.PasswordInput(), label='Confirme Contraseña')

	class Meta:
		model = User
		fields = ('email', 'username', 'password',)
		widgets = {
			'email': forms.EmailInput(),
			'password': forms.PasswordInput(),
		}
		labels = {
			'email': 'Correo Electrónico',
			'password': 'Contraseña',
		}

#Formulario de datos de cliente
class ClienteForm(forms.ModelForm):

	class Meta:
		model = Cliente
		fields = ('rif', 'cargo','telefono')
		widgets = {
			'cargo': forms.Select(),
		}
		labels = {
			'telefono': 'Teléfono',
		}

	def __init__(self, *args, **kwargs):
		super(ClienteForm, self).__init__(*args, **kwargs)
		instance = getattr(self, 'instance', None)
		if instance and instance.pk:
			self.fields['rif'].widget.attrs['readonly'] = True

	def clean_username(self):
		instance = getattr(self, 'instance', None)
		if instance and instance.pk:
			return instance.rif
		else:
			return self.cleaned_data['rif']


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
		('rest', 'Restaurante'), 
		('bar', 'Bar'), 
		('hel', 'Heladería'), 
		('pan', 'Panaderia'), 
		('cafe', 'Cafetería'),)
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


#Formulario para la creacion de usuario
class CuentaForm(ModelForm):

	class Meta:
		model = User
		fields = ('username', 'email')

		cargo = forms.CharField(max_length=20)
		rif = forms.CharField(max_length=13)