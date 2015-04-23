# -*- coding: utf-8 -*-
from django.forms import ModelForm, Textarea
from django import forms
from models import *
from menu2cero.apps.main.models import *
from django.forms.extras.widgets import *
from django.contrib.auth.forms import UserCreationForm

#Formulario para el login de usuario 				
class LoginForm(forms.ModelForm):

	class Meta:
		model = User
		fields = ('email','password')
		widgets = {
			'password': forms.PasswordInput(attrs={'class':"form-control", 'placeholder':"Contraseña"}),
			'email': forms.EmailInput(attrs={'class':"form-control", 'placeholder':"Correo"}),
		}


#Formulario de registro simple de usuario
class EditUserForm(ModelForm):

	class Meta:
		model = User
		fields = ('email', 'nombre',)
		widgets = {
			'email': forms.EmailInput(),
		}
		labels = {
			'email': 'Correo Electrónico',
		}

	def __init__(self, *args, **kwargs):
		super(EditUserForm, self).__init__(*args, **kwargs)
		instance = getattr(self, 'instance', None)
		if instance and instance.pk:
			self.fields['email'].widget.attrs['readonly'] = True

	def clean_username(self):
		instance = getattr(self, 'instance', None)
		if instance and instance.pk:
			return instance.username
		else:
			return self.cleaned_data['username']


#Formularios del perfil del usuario de los restaurantes

#Formulario de informacion principal
class PrincipalForm(forms.ModelForm):

	class Meta:
		model = Restaurante
		fields = ('nombre', 'categoria')
		widgets = {
			'nombre' : forms.TextInput(attrs={'placeholder':'Nombre de su restaurante'}),
			'categoria': forms.CheckboxSelectMultiple()
		}

	def clean_categoria(self):
		categoria = self.cleaned_data.get("categoria")

		if len(categoria) > 3:
			raise forms.ValidationError(u"El máximo de categorías a elegir es 3.")
		return categoria


#Formulario de los horarios
class HorariosForm(forms.Form):

	horas = (('','- hora -'), ('1:00 am', '1:00 am'), ('2:00 am', '2:00 am'),
		('3:00 am', '3:00 am'), ('4:00 am', '4:00 am'), ('5:00 am', '5:00 am'),
		('6:00 am', '6:00 am'), ('7:00 am', '7:00 am'), ('8:00 am', '8:00 am'),
		('9:00 am', '9:00 am'), ('10:00  am', '10:00  am'), ('11:00 am', '11:00 am'),
		('12:00 pm', '12:00 pm'), ('1:00 pm', '1:00 pm'), ('2:00 pm', '2:00 pm'),
		('3:00 pm', '3:00 pm'), ('4:00 pm', '4:00 pm'), ('5:00 pm', '5:00 pm'),
		('6:00 pm', '6:00 pm'), ('7:00 pm', '7:00 pm'),('8:00 pm', '8:00 pm'),
		('9:00 pm', '9:00 pm'), ('10:00 pm', '10:00 pm'), ('11:00 pm', '11:00 pm'), 
		('12:00 am', '12:00 am'),)


	lunes_desde = forms.ChoiceField(choices=horas)
	lunes_hasta = forms.ChoiceField(choices=horas)

	martes_desde = forms.ChoiceField(choices=horas)
	martes_hasta = forms.ChoiceField(choices=horas)

	miercoles_desde = forms.ChoiceField(choices=horas)
	miercoles_hasta = forms.ChoiceField(choices=horas)

	jueves_desde = forms.ChoiceField(choices=horas)
	jueves_hasta = forms.ChoiceField(choices=horas)

	viernes_desde = forms.ChoiceField(choices=horas)
	viernes_hasta = forms.ChoiceField(choices=horas)

	sabado_desde = forms.ChoiceField(choices=horas)
	sabado_hasta = forms.ChoiceField(choices=horas)

	domingo_desde = forms.ChoiceField(choices=horas)
	domingo_hasta = forms.ChoiceField(choices=horas)


#Formulario de la direccion del restaurante
class DireccionForm(forms.ModelForm):

	class Meta:
		model = Direccion
		fields = ( 
			'ciudad', 
			'zona',
			'calle',
			'latitud',
			'longitud',
		)
		widgets = {
			'ciudad': forms.Select(attrs={'class':"form-control", 'placeholder': 'Ciudad'}),
			'zona': forms.Select(attrs={'class':"form-control", 'placeholder':'Zona'}),
			'calle': forms.Textarea(attrs={'class':"form-control", 'rows':'4', 'placeholder':'Calle o avenida'})
		}


#Formulario del telefono del restaurante
class TelefonoRestauranteForm(forms.ModelForm):

	class Meta:
		model = TelefonoRestaurante
		fields = (
			'numero',
			'display'
		)
		widgets = {
			'restaurante': forms.HiddenInput(),
			'numero': forms.TextInput(attrs={'class':'form-control'}),
			'display': forms.CheckboxInput(attrs={'class':'checkbox'})
		}


#Formulario de otra informacion del restaurante
class DescripcionForm(forms.Form):
	
	descripcion_rest = forms.CharField(max_length=300,widget=forms.Textarea(attrs={'placeholder':"Breve retrato que describe su restaurante",'class':"form-control"}))
	servicios = forms.ModelMultipleChoiceField(queryset=Servicio.objects.all(), widget=forms.CheckboxSelectMultiple())
	metodos_de_pago = forms.ModelMultipleChoiceField(queryset=Metodo.objects.all(), widget=forms.CheckboxSelectMultiple())


#Formulario de redes sociales
class RedesForm(forms.ModelForm):

	class Meta:
		model = Red_social
		fields = ('facebook', 'twitter', 'instagram')
		widgets = {
			'facebook': forms.TextInput(attrs={'class':"form-control", 'placeholder':"facebook"}),
			'twitter': forms.TextInput(attrs={'class':"form-control", 'placeholder':"twitter"}),
			'instagram': forms.TextInput(attrs={'class':"form-control", 'placeholder':"instagram"}),
		}


#Formulario para el logo del restaurante
class logoRestForm(forms.ModelForm):

	class Meta:
		model = Restaurante
		fields = ('logo',)


#Formulario de logo del restaurante
class LogosForm(forms.Form):

	choices_logos = (('Menu2cero', 'Menu2cero'), ('Desayuno', 'Desayuno'), ('Rapida', u'Rápida'), ('Carnes', 'Carnes'), 
		('Asiatica', u'Asiática'), ('Bar', 'Bar'), ('Italiana', 'Italiana'),)

	logos = forms.ChoiceField(choices=choices_logos, widget=forms.RadioSelect())


#Formulario de imagen del restaurante
class ImagenForm(forms.ModelForm):

	class Meta:
		model = Imagen
		fields = ('archivo', 'descripcion', 'thumbnail')
		widgets = {
			'descripcion': forms.TextInput(attrs={'class':"form-control"}),
			'thumbnail': forms.FileInput(attrs={'style':"display:none"}),
		}
		labels = {
			'archivo': 'Imágen',
			'descripcion': 'Descripción de imágen',
			'thumbnail': '',
		}


#Formulario del menu del restaurante
class MenuForm(forms.ModelForm):

	class Meta:
		model = Menu
		fields = ('nombre',)


#Formulario de los platos del menu
class PlatosForm(forms.ModelForm):

	class Meta:
		model = Plato
		fields = ( 'nombre', 'descripcion', 'tipo', 'precio', 'imagen')
		widgets = {
			'nombre': forms.TextInput(attrs={'class':"form-control"}),
			'descripcion': forms.Textarea(attrs={'class':"form-control"}),
			'tipo': forms.Select(attrs={'class':'form-control'}),
			'precio': forms.NumberInput(attrs={'class':"form-control"}),
			'imagen': forms.FileInput(attrs={'disabled':'True'})
		}
		

#Formulario para los tipos de platos
class TipoPlatoForm(forms.Form):

	nombre = forms.ModelChoiceField(queryset=Tipo.objects.all().values_list('nombre', flat=True).distinct().order_by('nombre'), empty_label='- Tipo -', required=True)


#Formulario de eliminacion de restaurante
class EliminarForm(forms.Form):

	eliminar = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'type':'hidden'}), required=False)