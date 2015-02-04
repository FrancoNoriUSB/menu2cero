# -*- coding: utf-8 -*-
from django.utils.translation import gettext as _
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

#Modelos de la base de datos de Menu 2.0

#Manejador de la clase user
class UserManager(BaseUserManager):
	def create_user(self, nombre, email, password):
		if not email:
			raise ValueError("Por favor ingrese un correo válido.")

		user = self.model(
			email = self.normalize_email(email),
			nombre = nombre,
			)
		user.set_password(password)
		user.save()
		return user

	def create_superuser(self, nombre, email, password):
		user = self.model(
			email = self.normalize_email(email),
			nombre = nombre,
		)
		user.set_password(password)
		user.is_staff = True
		user.save()
		return user


# Definicion del usuario
class User(AbstractBaseUser):

	nombre = models.CharField(max_length=40)
	email = models.EmailField(unique=True)
	is_staff = models.BooleanField(default=False)
	is_active = models.BooleanField(default=True)

	USERNAME_FIELD = "email"
	REQUIRED_FIELDS = ['nombre', 'password',]

	objects = UserManager()

	def get_full_name(self):
		return self.email

	def get_short_name(self):
		return self.email

	def __str__(self):
		return self.email

	def has_perm(self, obj=None):
		return self.is_staff

	def has_module_perms(self, package):
		return self.is_staff


#Clase para los planes que tendran los restaurantes
class Plan(models.Model):

	posicionamientos = (
		('Bajo','Bajo'),
		('Medio','Medio'),
		('Alto','Alto'),
	)

	nombre = models.CharField(max_length=30)
	descripcion = models.CharField(max_length=300)
	max_imagenes = models.IntegerField(max_length=3)
	estadisticas = models.BooleanField(default=False)
	posicionamiento = models.CharField(max_length=10, choices=posicionamientos, default='N/A')
	boletin = models.BooleanField(default=False)
	impresion = models.BooleanField(default=False)
	costo = models.DecimalField(max_digits=10, decimal_places=2)

	class Meta:
		ordering = ('nombre',)
		verbose_name = _('Plan')
		verbose_name_plural = _('Planes')

	def __unicode__(self):
		return u"Plan: %s. Costo: %s" %(self.nombre, self.costo)


#Clase para las categorias de los restaurantes
class Categoria(models.Model):

	nombre = models.CharField(max_length=30, unique=True)
	imagen = models.ImageField(upload_to='uploads/img/categorias')

	class Meta:
		ordering = ('nombre',)
		verbose_name = _(u'Categoría')
		verbose_name_plural = _(u'Categorías')

	def __unicode__(self):
		return u"%s" %(self.nombre)
	

#Clase para los servicios de los restaurantes
class Servicio(models.Model):
	
	nombre = models.CharField(max_length=30)

	class Meta:
		ordering = ('nombre',)
		verbose_name = _('Servicio')
		verbose_name_plural = _('Servicios')

	def __unicode__(self):
		return u"%s" %(self.nombre)


#Clase para los metodos de pago que utilizan los restaurantes
class Metodo(models.Model):
	pagos = (
		('Efectivo', 'Efectivo'), 
		('Debito', u'Débito'), 
		('Credito', u'Crédito'), 
		('Cesta Ticket', 'Cesta Ticket'),
	)
	
	nombre = models.CharField(max_length=12, choices=pagos)
	
	class Meta:
		ordering = ('nombre',)
		verbose_name = _(u'Método')
		verbose_name_plural = _(u'Métodos')

	def __unicode__(self):
		return u"%s" %(self.nombre)


#Clase del cliente
class Cliente(models.Model):

	cargos = (
		('', '- Cargo -'),
		('Gerente','Gerente'),
		('Encargado', 'Encargado'),
		(u'Dueño', u'Dueño'),
	)

	cargo = models.CharField(max_length=20, choices=cargos)
	telefono = models.CharField(max_length=20)

	#Claves foraneas y de otras tablas
	user = models.OneToOneField(User)

	class Meta:
		ordering = ('user',)
		verbose_name = _('Cliente')
		verbose_name_plural = _('Clientes')

	def __unicode__(self):
		return u"Nombre: %s" %(self.user.username)


#Clase del restaurante
class Restaurante(models.Model):
	
	tipos = (
		('Restaurante', 'Restaurante'),
		('Bar', 'Bar'),
		(u'Heladería', u'Heladería'),
		('Panadería', u'Panadería'),
		(u'café', 'Cafetería'),
	)

	statuses = (
		('Activo', 'Activo'),
		('Inactivo', 'Inactivo'),
		('Eliminado', 'Eliminado'),
	)

	visible = (
		(u'Público','Público'),
		('Privado','Privado'),
	)

	rif = models.CharField(max_length=13)
	nombre = models.CharField(max_length=50, help_text='Introduzca el nombre de su restaurante.')
	logo = models.ImageField(upload_to='uploads/img/logos/', default='uploads/img/logos/ico.png')
	descripcion = models.TextField(max_length=300)
	status = models.CharField(max_length=20, default='Activo', choices=statuses, editable=False)
	tipo = models.CharField(max_length=4, choices=tipos)
	abierto = models.BooleanField(default=True, help_text='Desmarcar si su restaurante se encuentra cerrado')
	visibilidad = models.CharField(max_length=10, null=True, choices=visible)
	
	#Claves foraneas y de otras tablas
	cliente = models.ForeignKey(Cliente)	
	categoria = models.ManyToManyField(Categoria)
	servicios = models.ManyToManyField(Servicio)
	metodos_pago = models.ManyToManyField(Metodo)
	plan = models.ForeignKey(Plan)

	class Meta:
		ordering = ('nombre',)
		verbose_name = _('Restaurante')
		verbose_name_plural = _('Restaurantes')

	def __unicode__(self):
		return u"Nombre: %s. Dueno: %s" %(self.nombre, self.cliente)


#Clase para las ciudades de los restaurantes
class Ciudad(models.Model):

	nombre = models.CharField(max_length=30)

	class Meta:
		ordering = ('nombre',)
		verbose_name = "Ciudad"
		verbose_name_plural = "Ciudades"

	def __unicode__(self):
		return u"%s" %(self.nombre)


#Clase para las zonas de las ciudades
class Zona(models.Model):

	nombre = models.CharField(max_length=50)

	#Claves foraneas y de otras tablas
	ciudad = models.ForeignKey(Ciudad)

	class Meta:
		ordering = ('nombre',)
		verbose_name = "Zona"
		verbose_name_plural = "Zonas"

	def __unicode__(self):
		return u"%s" %(self.nombre)
	

#Clase para la direccion del restaurante
class Direccion(models.Model):

	coord = models.CharField(max_length=50)
	direccion = models.CharField(max_length=100)

	#Claves foraneas y de otras tablas
	ciudad = models.ForeignKey(Ciudad)
	zona = models.ForeignKey(Zona)
	restaurante = models.OneToOneField(Restaurante)

	class Meta:
		ordering = ('ciudad',)
		verbose_name = _(u'Dirección')
		verbose_name_plural = _('Direcciones')

	def __unicode__(self):
		return u"%s" %(self.direccion)


#Clase para las redes sociales del restaurante
class Red_social(models.Model):

	facebook = models.CharField(max_length=100, null=True)
	twitter = models.CharField(max_length=50, null=True)
	instagram = models.CharField(max_length=50, null=True)

	#Claves foraneas y de otras tablas
	restaurante = models.OneToOneField(Restaurante)

	class Meta:
		ordering = ('facebook',)
		verbose_name = _('Red_social')
		verbose_name_plural = _('Redes_sociales')

	def __unicode__(self):
		return u"fb: %s. tw: %s" %( self.facebook, self.twitter)


#Clase abstracta de telefonos que tienen los restaurantes o clientes
class Telefono(models.Model):

	numero = models.CharField(max_length=20)

	class Meta:
		abstract = True
		ordering = ('numero',)
		verbose_name = _(u'Teléfono')
		verbose_name_plural = _(u'Teléfonos')

	def __unicode__(self):
		return u"Telefono: %s" %(self.numero)


#Clase concreta del telefono de los restaurantes
class TelefonoRestaurante(Telefono):

	display = models.BooleanField(default=True, help_text='Marcado si desea que se muestre en el perfil')

	#Claves foraneas y de otras tablas
	restaurante = models.ForeignKey(Restaurante, related_name='telefonos')

	class Meta(Telefono.Meta):
		abstract = False


#Clase de las imagenes de los restaurantes
class Imagen(models.Model):
	
	imagen = models.ImageField(upload_to='uploads/img/rest/')
	thumbnail = models.ImageField(upload_to='uploads/img/rest/thumbnails/', blank=True,null=True)
	descripcion = models.CharField(max_length=140, null=True)

	#Claves foraneas y de otras tablas
	restaurante = models.ForeignKey(Restaurante)

	def create_thumbnail(self):

		# If there is no image associated with this.
		# do not create thumbnail
		if not self.imagen:
			return
 
		from PIL import Image
		from cStringIO import StringIO
		from django.core.files.uploadedfile import SimpleUploadedFile
		import os
 
		# Set our max thumbnail size in a tuple (max width, max height)
		THUMBNAIL_SIZE = (200,200)

		# Open original photo which we want to thumbnail using PIL's Image
		imagen = Image.open(StringIO(self.imagen.read()))
		image_type = imagen.format.lower()

		imagen.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)
 
		# Save the thumbnail
		temp_handle = StringIO()
		imagen.save(temp_handle, image_type)
		temp_handle.seek(0)
 
		# Save image to a SimpleUploadedFile which can be saved into
		# ImageField
		suf = SimpleUploadedFile(os.path.split(self.imagen.name)[-1], temp_handle.read(), content_type='image/%s' % (image_type))
		# Save SimpleUploadedFile into image field
		self.thumbnail.save('%s_thumbnail.%s'%
			(os.path.splitext(suf.name)[0], image_type), suf, save=False)

	def save(self):
		# create a thumbnail
		self.create_thumbnail()
		super(Imagen, self).save()

	class Meta:
		ordering = ('imagen',)
		verbose_name = _(u'Imágen')
		verbose_name_plural = _(u'Imágenes')

	def __unicode__(self):
		return u"Imagen Restaurante: %s" %(self.restaurante)


#Clase del comensal
class Comensal(models.Model):

	ip = models.CharField(primary_key=True, max_length=15)
	status = models.CharField(max_length=20, null=True)

	#Claves foraneas y de otras tablas
	restaurante = models.ManyToManyField(Restaurante)

	class Meta:
		ordering = ('ip',)
		verbose_name = _('Comensal')
		verbose_name_plural = _('Comensales')

	def __unicode__(self):
		return u"Restaurante: %s. Ip: %s" %(self.restaurante, self.ip)


#Clase para los distintos horarios que habre un restaurante
class Horario(models.Model):

	dia = models.CharField(max_length=10)
	desde = models.CharField(max_length=20)
	hasta = models.CharField(max_length=20)

	#Claves foraneas de otras tablas
	restaurante = models.ForeignKey(Restaurante)

	class Meta:
		ordering = ('restaurante',)
		verbose_name = _('Horario')
		verbose_name_plural = _('Horarios')

	def __unicode__(self):
		return u"%s: %s %s %s" %(self.restaurante.nombre, self.dia, self.desde, self.hasta)


#Clase para los menus de los restaurantes
class Menu(models.Model):

	nombre = models.CharField(max_length=20)

	#Claves foraneas y de otras tablas
	restaurante = models.ForeignKey(Restaurante)

	class Meta:
		ordering = ('restaurante',)
		verbose_name = _(u'Menú')
		verbose_name_plural = _(u'Menús')

	def __unicode__(self):
		return u"%s" %(self.restaurante)


#Modelo para los tipos de platos
class Tipo(models.Model):

	nombre =  models.CharField(max_length=50)

	class Meta:
		ordering = ('nombre',)
		verbose_name = _('Tipo')
		verbose_name_plural = _('Tipos')

	def __unicode__(self):
		return u"%s" %(self.nombre)


#Clase para los platos de los menus
class Plato(models.Model):
	
	nombre = models.CharField(max_length=30)
	descripcion = models.CharField(max_length=300)
	precio = models.DecimalField(max_digits=10, decimal_places=2)
	disponibilidad = models.BooleanField(default=True, help_text='Desmarque si el plato no se encuentra disponible')
	imagen = models.ImageField(upload_to='uploads/img/menus/', default='')

	#Claves foraneas y de otras tablas
	tipo = models.ForeignKey(Tipo)
	menu = models.ForeignKey(Menu)

	class Meta:
		ordering = ('nombre',)
		verbose_name = _('Plato')
		verbose_name_plural = _('Platos')

	def __unicode__(self):
		return u"Plato: %s. Precio: %s. %s" %(self.nombre, self.precio, self.menu)


#Clase para los pagos de los clientes
class Pago(models.Model):
	
	tipos = ( 
		('mensual', 'mensual'),
		('trimestral', 'trimestral'),
		('semanal', 'semestral'),
		('anual', 'anual'),
	)

	monto = models.DecimalField(max_digits=10, decimal_places=2)
	fecha = models.DateField(auto_now_add=True)
	vigencia = models.DateField(auto_now_add=False)
	tipo = models.CharField(choices=tipos, max_length=3)
	numero = models.DecimalField(max_digits=20, decimal_places=2)

	#Claves foraneas y de otras tablas
	cliente = models.ForeignKey(Cliente)
	restaurante = models.ForeignKey(Restaurante)

	class Meta:
		ordering = ('fecha',)
		verbose_name = _('Pago')
		verbose_name_plural = _('Pagos')

	def __unicode__(self):
		return u"Cliente: %s. Fecha: %s. Monto: %s" %(self.cliente, self.fecha, self.monto)


#Clase para los votos que emiten los usuarios hacia los restaurantes
class Voto(models.Model):

	valor = models.DecimalField(max_digits=2, decimal_places=1)

	#Claves foraneas y de otras tablas
	restaurante = models.ForeignKey(Restaurante)

	class Meta:
		verbose_name = _('Voto')
		verbose_name_plural = _('Votos')

	def __unicode__(self):
		return u'Voto %s' %(self.valor)