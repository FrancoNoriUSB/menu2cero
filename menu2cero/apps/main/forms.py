# -*- coding: utf-8 -*-
from django.forms import ModelForm, Textarea
from django import forms
from models import *
from django.forms.extras.widgets import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm

#Formulario de registro sumple de usuario
class RegistroForm(ModelForm):
	nombre_de_usuario = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'readonly':'readonly'}))
	rif = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'readonly':'readonly'}))
	cargo = forms.CharField(max_length=30)
	telefono = forms.CharField(max_length=20, required=False)

	class Meta:
		model = User
		fields = ('email',)
		widgets = {
	    'email': forms.EmailInput(),
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

	Ciudad = forms.ModelChoiceField(queryset=Direccion.objects.all().values_list('ciudad', flat=True).distinct().order_by('ciudad'), empty_label='- Ciudad -', required=False, to_field_name="ciudad")

	Zona = forms.ModelChoiceField(queryset=Direccion.objects.all().values_list('zona', flat=True).distinct().order_by('zona'), empty_label='- Zona -', required=False, to_field_name="zona")

	Tipo = forms.ChoiceField(choices=choices_tipo, required=False)

	Servicios = forms.MultipleChoiceField(choices=choices_servicios, widget=forms.CheckboxSelectMultiple, required=False)


#Formulario para la creacion de usuario
class CuentaForm(ModelForm):

	class Meta:
		model = User
		fields = ('username', 'email')

		cargo = forms.CharField(max_length=20)
		rif = forms.CharField(max_length=13)