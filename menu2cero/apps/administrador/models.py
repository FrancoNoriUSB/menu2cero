# -*- coding: utf-8 -*-
from django.utils.translation import gettext as _
from django.db import models
from menu2cero.apps.main.models import *
# Create your models here.

#Clase para los usuarios que administraran la app
class Administrador(models.Model):

	nombre = models.CharField(max_length=30)
	correo = models.EmailField(max_length=75, primary_key=True)
	nivel = models.DecimalField(max_digits=2, decimal_places=0)

	#Claves foraneas y de otras tablas
	user = models.OneToOneField(User)

	class Meta:
		ordering = ('nombre',)
		verbose_name = _('Administrador')
		verbose_name_plural = _('Administradores')

	def __unicode__(self):
		return u"Admin: %s" %(self.nombre)