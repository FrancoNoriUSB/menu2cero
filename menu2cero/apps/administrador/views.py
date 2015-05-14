# -*- coding: utf-8 -*-

# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.template.loader import get_template
from django.template import Context
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from menu2cero.apps.main.models import *
from menu2cero.apps.main.forms import *
from menu2cero.apps.administrador.forms import *
from django.db.models import Count
from django.db.models import Q
from datetime import datetime, date
from django.forms.models import inlineformset_factory

#Mercadopago
import mercadopago
import json
import os, sys

mp = mercadopago.MP("2041234873847333", "dcFLGjyBjtk5dOfN4rC16s45a3mECeaA")

#Vista para el ingreso de los usuarios.
def loginUser(request):

	email = ''
	password = ''

	if request.user.is_authenticated() and request.user:
		return True
	else:
		email = request.POST['email']
		password = request.POST['password']
		usuario = authenticate(email=email, password=password)
		if usuario:
			# Caso del usuario activo
			if usuario.is_active:
				login(request, usuario)
				return True
			else:
				return "Tu cuenta esta bloqueada"
		else:
			# Usuario invalido o no existe!
			print "Invalid login details: {0}, {1}".format(email, password)

	return False

#Vista del perfil del usuario logueado
@login_required
def admin_perfil_view(request):

	#Variables y Formularios
	cliente = get_object_or_404(Cliente, user=request.user)
	buscadorF = BuscadorForm()
	eliminarF = EliminarForm()
	logosF = LogosForm()
	clienteF = ClienteForm(instance=cliente, initial={
		'cargo':cliente.cargo,
		'telefono':cliente.telefono
		})

	euserF = EditUserForm(instance=cliente.user, initial={
		'email':cliente.user.email,
		'username':cliente.user.nombre,
		})
	modificarF = modificarContrasenaForm(user=cliente.user)
	restaurantes = []
	restaurantes_list = []
	error = ''
	guardado = ''
	vencidos = []

	#Caso para el buscador
	if request.method == 'POST':
		buscadorF = BuscadorForm(request.POST)
		modificarF = modificarContrasenaForm(request.POST)
		clienteF = ClienteForm(request.POST, instance=cliente)
		euserF = EditUserForm(request.POST, instance=cliente.user)

		if buscadorF.is_valid():
			filtro = FiltroForm(request.POST)
			palabra = "buscar_"+buscador.cleaned_data['palabra']
			return redirect('restaurantes', palabra=palabra)

		elif modificarF.is_valid():
			modificarF.save()

		elif clienteF.is_valid() and euserF.is_valid():
			clienteF.save()
			euserF.save()
			guardado = 'Se ha guardado la información con éxito!'

	usuario = request.user

	#Restaurantes del cliente logueado
	try:
		restaurantes = Restaurante.objects.filter(cliente__user_id=usuario.id).exclude(status='Eliminado')
	except:
		error = 'Cliente no posee restaurantes'

	#Votacion de cada restaurante
	for restaurante in restaurantes:
		votacion = 0
		cantidad = 0
		for voto in restaurante.votos.all():
			votacion += voto.valor
			cantidad += 1

		#Verificacion de que existe al menos un voto
		if cantidad != 0:
			votacion = '%.1f'%(float(votacion/cantidad))

		restaurantes_list.append((restaurante,votacion))

	#Cliente logueado en cuestion
	try:
		cliente = Cliente.objects.get(user_id=usuario.id)
	except:
		error = 'Cliente no posee usuario!'

	#Pagos realizados por el cliente
	pagos = Pago.objects.filter(cliente__user_id=usuario.id)
	for pago in pagos:
		if pago.vigencia <= date.today():
			vencidos.append((pago.vigencia, pago.restaurante.nombre))

	#Pagos asociados a cada restaurante
	ctx = {
		'buscador':buscadorF,
		'EliminarForm':eliminarF, 
		'LogosForm':logosF,
		'ClienteForm':clienteF,
		'EditUserForm':euserF,
		'modificarContrasenaForm': modificarF,
		'restaurantes':restaurantes_list, 
		'cliente': cliente,
		'vencidos': vencidos,
		'guardado':guardado,
	}
	return render_to_response('administrador/perfil/perfil.html', ctx, context_instance=RequestContext(request))

#View de agregar el restaurante (simplemente inicializa la vista)
@login_required
def admin_agregar_restaurante_view(request):

	#Declaracion de variables
	lat = 10.4683918
	lng = -66.8903658

	#Formularios basicos
	buscadorF = BuscadorForm()
	principalF = PrincipalForm()
	horariosF = HorariosForm()
	direccionF = DireccionForm()

	#Telefonos del restaurante
	telefonoFormSet = inlineformset_factory(Restaurante, TelefonoRestaurante, TelefonoRestauranteForm, can_delete=False, extra=1)
	telefonoF = telefonoFormSet()

	#Formularios otra informacion
	descripcionF = DescripcionForm()
	redesF = RedesForm()

	#Formularios de imagenes
	logosF = LogosForm()
	imagenF = ImagenForm()

	#Verificacion de que se enviaron los formularios
	if request.POST:
		principalF = PrincipalForm(request.POST)
		horariosF = HorariosForm(request.POST)
		direccionF = DireccionForm(request.POST)
		telefonoFormSet = inlineformset_factory(Restaurante, TelefonoRestaurante, TelefonoRestauranteForm, can_delete=False)
		telefonoF = telefonoFormSet(request.POST)

		#Verificacion de que los campos de los formularios se llenaron
		if principalF.is_valid() and horariosF.is_valid() and direccionF.is_valid() and telefonoF.is_valid():
			id_restaurante = restaurante_info_basica(request, 0, principalF, horariosF, direccionF, telefonoF)
			return  HttpResponseRedirect('/administrador/editar/'+str(id_restaurante)+'/0')

	ctx = {
		'buscador':buscadorF,
		'PrincipalForm':principalF,
		'HorariosForm':horariosF,
		'DireccionForm':direccionF,
		'TelefonoRestauranteForm': telefonoF,
		'DescripcionForm': descripcionF,
		'lat':lat,
		'lng':lng,
	}

	return render_to_response('administrador/agregar/agregar.html', ctx, context_instance=RequestContext(request))

#View de la edicion del restaurante (simplemente inicializa la vista)
@login_required
def admin_editar_restaurante_view(request, id_rest, formulario):

	#Declaracion de variables
	buscadorF = BuscadorForm()
	vencidos = []
	pago = []
	restaurante = []
	categorias_rest = []
	servicios_rest = []
	metodos_rest = []
	platos_data = []
	red_social = Red_social(facebook='', twitter='', instagram='')
	puntuacion = 0
	horarios = []
	dataHorarios = []
	formulario_activo = ''
	forms_platos = []

	#Verificacion de que el restaurante pertenece al usuario
	restaurante = get_object_or_404(Restaurante, cliente__user_id=request.user.id, id=id_rest)

	#Coordenadas del restaurante
	lat = restaurante.direccion.latitud
	lng = restaurante.direccion.longitud

	#Votos del restaurante
	votos = Voto.objects.filter(restaurante=restaurante)

	#Calculo de la puntuacion
	if len(votos) == 0:
		puntuacion = 0
	else:
		for voto in votos:
			puntuacion = puntuacion + voto.valor

		puntuacion = puntuacion/votos.count()

	#Estatus del plan
	try:
		pago = Pago.objects.get(restaurante__id=restaurante.id).order_by('id').reverse()
	except:
		error = 'No existen pagos para este restaurante'        

	#Pago vencido
	if pago != []:
		if pago.vigencia <= date.today():
			vencidos.append((pago.vigencia, pago.restaurante.nombre, pago.monto))

	#Formularios de info basica
	principalF = PrincipalForm(instance=restaurante)

	#Manejo de info para el horario del restaurante
	horarios = Horario.objects.filter(restaurante=restaurante).order_by("id")

	for horario in horarios:
		dataHorarios.append((horario.desde, horario.hasta))

	horarios = {
		'lunes_desde':dataHorarios[0][0], 'lunes_hasta':dataHorarios[0][1], 
		'martes_desde':dataHorarios[1][0],'martes_hasta':dataHorarios[1][1], 
		'miercoles_desde':dataHorarios[2][0], 'miercoles_hasta':dataHorarios[2][1], 
		'jueves_desde':dataHorarios[3][0], 'jueves_hasta':dataHorarios[3][1], 
		'viernes_desde':dataHorarios[4][0], 'viernes_hasta':dataHorarios[4][1], 
		'sabado_desde':dataHorarios[5][0], 'sabado_hasta':dataHorarios[5][1],
		'domingo_desde':dataHorarios[6][0], 'domingo_hasta':dataHorarios[6][1]
	}

	horariosF = HorariosForm(initial=horarios)

	direccionF = DireccionForm(instance=restaurante.direccion)

	#Telefonos del restaurante
	telefonoFormSet = inlineformset_factory(Restaurante, TelefonoRestaurante, TelefonoRestauranteForm, can_delete=False, extra=1, max_num=2)
	telefonoF = telefonoFormSet(instance=restaurante)

	categorias = Categoria.objects.filter(restaurante=restaurante)

	for categoria in categorias:
		categorias_rest.append(str(categoria.id).decode('unicode-escape'))

	#Inicializacion de los formularios de Otra Informacion
	servicios = Servicio.objects.filter(restaurante=restaurante)

	for servicio in servicios:
		servicios_rest.append(str(servicio.id).decode('unicode-escape'))

	metodos = Metodo.objects.filter(restaurante=restaurante)

	for metodo in metodos:
		metodos_rest.append(str(metodo.id).decode('unicode-escape'))

	descripcionF = DescripcionForm(initial={'descripcion_rest': restaurante.descripcion, 'servicios': servicios_rest, 'metodos_de_pago': metodos_rest})

	try:
		red_social = Red_social.objects.get(restaurante=id_rest)
	except:
		error = 'Este restaurante no posee red social'

	#Redes sociales del restaurante
	redesF = RedesForm(instance=red_social)

	#Inicializacion de los formularios de Imagenes
	logoRestF = logoRestForm(instance=restaurante)

	#Inicializacion de los formularios de imagenes
	logosF = LogosForm()

	#Inicializacion del formulario de imagenes de resturante
	imagenes = Imagen.objects.filter(restaurante=restaurante)
	imagenFormSet = inlineformset_factory(Restaurante, Imagen, form=ImagenForm, extra=1, max_num=restaurante.plan.max_imagenes, can_delete=True)
	imagenF = imagenFormSet(instance=restaurante, queryset=Imagen.objects.filter(restaurante=restaurante))

	#Inicializacion de los formularios del menu
	platos = Plato.objects.filter(menu__restaurante=restaurante).order_by('tipo__nombre')
	platosFormSet = inlineformset_factory(Menu, Plato, form = PlatosForm, extra=1, can_delete=False)

	try:
		menu = Menu.objects.get(restaurante=restaurante)
	except:
		menu = Menu()

	platosF = platosFormSet(instance=menu, queryset=Plato.objects.filter(menu__restaurante=restaurante).order_by('tipo'))

	#Revision si el plan actual del restaurante es Diamante
	if restaurante.plan.nombre != 'Diamante':
		for plato in platosF:
			plato.fields['imagen'] = forms.ImageField(widget=forms.HiddenInput())

	#Platos mas uno
	platos_list = []
	for plato in platos:
		platos_list.append(plato.tipo.nombre)
	platos_list.append('')

	#Arreglo de platos y form de platos
	forms_platos = zip(platosF.forms, platos_list)

	#Verificacion de envio de formularios de restaurante
	if request.POST:

		#Verificacion de cual formulario se envio
		if formulario == 'basico':
			principalF = PrincipalForm(request.POST, instance=restaurante)
			horariosF = HorariosForm(request.POST)
			direccionF = DireccionForm(request.POST, instance=restaurante.direccion)
			telefonoFormSet = inlineformset_factory(Restaurante, TelefonoRestaurante, TelefonoRestauranteForm, can_delete=True, extra=1, max_num=2)
			telefonoF = telefonoFormSet(request.POST, instance=restaurante)

			#Verificacion de que los campos de los formularios se llenaron correctamente
			if principalF.is_valid() and horariosF.is_valid() and direccionF.is_valid():
				if telefonoF.is_valid():
					id_rest = restaurante_info_basica(request, id_rest, principalF, horariosF, direccionF, telefonoF)
				else:
					id_rest = restaurante_info_basica(request, id_rest, principalF, horariosF, direccionF, '')
				return  HttpResponseRedirect('/administrador/editar/'+str(id_rest)+'/basico')
			elif not(principalF.is_valid() or horariosF.is_valid() or direccionF.is_valid() or telefonoF.is_valid()):
				principalF = PrincipalForm(instance=restaurante)
				horariosF = HorariosForm(initial=horarios)
				direccionF = DireccionForm(instance=restaurante.direccion)
				telefonoFormSet = inlineformset_factory(Restaurante, TelefonoRestaurante, TelefonoRestauranteForm, can_delete=True, extra=1, max_num=2)
				telefonoF = telefonoFormSet(instance=restaurante)

		elif formulario == 'otra':
			descripcionF = DescripcionForm(request.POST)
			try:
				redes = Red_social.objects.get(restaurante=restaurante)
			except:
				redes = []

			#Caso en el que el restaurante no tiene redes
			if redes != []:
				redesF = RedesForm(request.POST, instance=redes)
			else:
				redesF = RedesForm(request.POST)

			#Verificacion de envio de formularios de otra info
			if descripcionF.is_valid() and redesF.is_valid():
				restaurante_otra_info(request, id_rest, descripcionF, redesF)
				return  HttpResponseRedirect('/administrador/editar/'+str(id_rest)+'/otra')
			elif not(descripcionF.is_valid() or redesF.is_valid()):
				descripcionF = DescripcionForm(initial={'descripcion_rest': restaurante.descripcion, 'servicios': servicios_rest, 'metodos_de_pago': metodos_rest})
				redesF = RedesForm(instance=red_social)

		elif formulario == 'imagenes':
			#Verificacion de los formularis de imagenes
			logoRestF = logoRestForm(request.POST, request.FILES, instance=restaurante)
			logosF = LogosForm(request.POST)
			imagenesFormSet = inlineformset_factory(Restaurante, Imagen, form=ImagenForm, extra=1, max_num=restaurante.plan.max_imagenes, can_delete=True)
			imagenesF = imagenesFormSet(request.POST, request.FILES, instance=restaurante,  queryset=Imagen.objects.filter(restaurante=restaurante))

			#Caso en el que el rest agrego un logo en el formulario de logoRestF
			if logosF.is_valid():
				logo = logosF.cleaned_data['logos']
				Restaurante.objects.filter(id=restaurante.id).update(logo="files/img/"+str(logo)+".jpg")
				logoRestF = logoRestForm(instance=restaurante)
			elif logoRestF.is_valid():
				logoRestF.save()
				logosF = LogosForm()
			else:
				logoRestF = logoRestForm(instance=restaurante)

			#Caso en el que se agregaron imagenes al rest
			if imagenesF.is_valid():
				imagenesF.save()
				return  HttpResponseRedirect('/administrador/editar/'+str(id_rest)+'/imagenes')
			else:
				imagenFormSet = inlineformset_factory(Restaurante, Imagen, form=ImagenForm, extra=1, max_num=restaurante.plan.max_imagenes, can_delete=True)
				imagenF = imagenFormSet(instance=restaurante, queryset=Imagen.objects.filter(restaurante=restaurante))

		elif formulario == 'menu':
			platosFormSet = inlineformset_factory(Menu, Plato, form = PlatosForm, can_delete=False)
			platosF = platosFormSet(request.POST, request.FILES, instance=menu)

			if platosF.is_valid():
				# Se crea el menu si no existe
				if not menu.id:
					menu.restaurante = restaurante
					menu.nombre = restaurante.nombre
					menu.save()
				for plato in platosF:
					platos = plato.save(commit=False)
					platos.menu = menu
					platos.save()

				return HttpResponseRedirect('/administrador/editar/'+str(id_rest)+'/menu')
				
	ctx = {
		'buscador':buscadorF,
		'PrincipalForm':principalF, 
		'HorariosForm':horariosF,
		'DireccionForm':direccionF,
		'TelefonoRestauranteForm': telefonoF, 
		'DescripcionForm': descripcionF,
		'RedesForm': redesF, 
		'LogosForm': logosF, 
		'logoRestForm': logoRestF, 
		'ImagenForm':imagenF, 
		'platosForm': platosF,
		'restaurante':restaurante, 
		'votos':votos, 
		'puntuacion':puntuacion, 
		'vencidos':vencidos, 
		'lat':lat, 
		'lng':lng,
		'categorias':categorias_rest,
		'metodos':metodos_rest,
		'servicios':servicios_rest,
		'formulario_activo':formulario,
		'forms_platos':forms_platos,
	}

	return render_to_response('administrador/editar/editar.html', ctx, context_instance=RequestContext(request))


#Vista para el manejo (guardado) del formulario info basica del restaurante
@login_required
def restaurante_info_basica(request, id_rest, principalF, horariosF, direccionF, telefonoF):

	#Inicializacion de variables
	categorias_rest = []
	existe = True
	dias = []

	try:
		restaurante = Restaurante.objects.get(cliente__user_id=request.user.id, id=id_rest)
	except:
		restaurante = []

	#Caso en que se edita un restaurante
	if  id_rest != 0:

		#Manejo del formulario principal
		categorias = principalF.cleaned_data['categoria']

		#Manejo del formulario de horarios
		dias.append(('Lunes', horariosF.cleaned_data['lunes_desde'], horariosF.cleaned_data['lunes_hasta']))
		dias.append(('Martes', horariosF.cleaned_data['martes_desde'], horariosF.cleaned_data['martes_hasta']))
		dias.append((u'Miércoles', horariosF.cleaned_data['miercoles_desde'], horariosF.cleaned_data['miercoles_hasta']))
		dias.append(('Jueves', horariosF.cleaned_data['jueves_desde'], horariosF.cleaned_data['jueves_hasta']))
		dias.append(('Viernes', horariosF.cleaned_data['viernes_desde'], horariosF.cleaned_data['viernes_hasta']))
		dias.append((u'Sábado', horariosF.cleaned_data['sabado_desde'], horariosF.cleaned_data['sabado_hasta']))
		dias.append(('Domingo', horariosF.cleaned_data['domingo_desde'],horariosF.cleaned_data['domingo_hasta']))

		for dia in dias:
			Horario.objects.filter(dia=dia[0], restaurante=restaurante).update(dia=dia[0], desde=dia[1], hasta=dia[2], restaurante=restaurante)

		cats = Categoria.objects.filter(restaurante=restaurante)

		for categoria in cats:
			categorias_rest.append(str(categoria.id).decode('unicode-escape'))

		#Caso para guardar solamente cuando cambiaron las categorias
		if categorias_rest != categorias:
			restaurante.categoria = categorias
			restaurante.save()

		#Manejo del formulario de telefonos
		if telefonoF !='':
			for form in telefonoF:
				telefono = form.save(commit=False)
				telefono.restaurante = restaurante
				telefono.save()

		#Manejo del formulario de direcciones
		direccionF.save()

		return id_rest

	#Caso en el que se agrega un restaurante
	elif id_rest == 0:

		categorias = principalF.cleaned_data['categoria']

		#Datos del restaurante
		restaurante = principalF.save(commit=False)
		restaurante.descripcion = u'<Este restaurante no posee descripción en estos momentos.>'
		restaurante.status = 'Activo'
		restaurante.tipo = 'rest'
		restaurante.abierto = True
		restaurante.visibilidad = 'Privado'
		restaurante.cliente = Cliente.objects.get(user=request.user.id)
		restaurante.plan = Plan.objects.get(id=1)
		restaurante.save()
		id_rest = restaurante.id
		
		for categoria in categorias:
			categorias_rest.append(str(categoria.id).decode('unicode-escape'))

		restaurante.categoria = categorias_rest

		#Manejo del formulario de telefonos
		if telefonoF !='':
			for form in telefonoF:
				telefono = form.save(commit=False)
				telefono.restaurante = restaurante
				telefono.save()

		#Manejo del formulario de horarios
		dias.append(('Lunes', horariosF.cleaned_data['lunes_desde'], horariosF.cleaned_data['lunes_hasta']))
		dias.append(('Martes', horariosF.cleaned_data['martes_desde'], horariosF.cleaned_data['martes_hasta']))
		dias.append((u'Miércoles', horariosF.cleaned_data['miercoles_desde'], horariosF.cleaned_data['miercoles_hasta']))
		dias.append(('Jueves', horariosF.cleaned_data['jueves_desde'], horariosF.cleaned_data['jueves_hasta']))
		dias.append(('Viernes', horariosF.cleaned_data['viernes_desde'], horariosF.cleaned_data['viernes_hasta']))
		dias.append((u'Sábado', horariosF.cleaned_data['sabado_desde'], horariosF.cleaned_data['sabado_hasta']))
		dias.append(('Domingo', horariosF.cleaned_data['domingo_desde'],horariosF.cleaned_data['domingo_hasta']))

		for dia in dias:
			horario = Horario(dia=dia[0], desde=dia[1], hasta=dia[2], restaurante=restaurante)
			horario.save()

		#Manejo del formulario de direcciones
		direccion =  direccionF.save(commit=False)
		direccion.restaurante = restaurante
		direccion.save()

		return id_rest


#Vista para el manejo (guardado) del formulario otra info del restaurante
@login_required
def restaurante_otra_info(request, id_rest, descripcionF, redesF):

	#Inicializacion de variables
	restaurante = get_object_or_404(Restaurante, id=id_rest)

	try:
		redes = Red_social.objects.get(restaurante=restaurante)
	except:
		redes = []

	restaurante.descripcion = descripcionF.cleaned_data['descripcion_rest']
	restaurante.servicios = descripcionF.cleaned_data['servicios']
	restaurante.metodos_pago = descripcionF.cleaned_data['metodos_de_pago']
	restaurante.save()

	#Caso en el que la red ya existe
	if redes != []:
		redesF.save()

	#Caso en el que no existe red aun
	else:
		redes = redesF.save(commit=False)
		redes.restaurante = restaurante
		redes.save()

	return True


#View para manejar el cierre del restaurante
@login_required
def visibilidad_restaurante(request, id_rest):

	restaurante = get_object_or_404(Restaurante, cliente__user_id=request.user.id, id=id_rest)

	if restaurante.visibilidad == 'Privado':
		restaurante.visibilidad = 'Público'
		restaurante.save()
	else:
		restaurante.visibilidad = 'Privado'
		restaurante.save()

	return HttpResponseRedirect('/administrador/perfil')


#View para manejar el cierre del restaurante
@login_required
def abrir_cerrar_restaurante(request, id_rest):

	restaurante = get_object_or_404(Restaurante, cliente__user_id=request.user.id, id=id_rest)
	restaurante.abierto = not(restaurante.abierto)
	restaurante.save()
	return HttpResponseRedirect('/administrador/perfil')


#View para eliminar el restaurante
@login_required
def eliminar_restaurante(request, id_rest):

	restaurante = get_object_or_404(Restaurante, cliente__user_id=request.user.id, id=id_rest)
	restaurante.status = 'Eliminado'
	restaurante.save()
	return HttpResponseRedirect('/administrador/perfil')


#View para cerrar la sesion
@login_required
def cerrar_sesion(request):

	logout(request)
	return HttpResponseRedirect('/')


#View para cambiar o asignar un plan
@login_required
def admin_plan_view(request, id_rest):
	restaurante = get_object_or_404(Restaurante, cliente__user_id=request.user.id, id=id_rest)

	#Formularios basicos
	buscadorF = BuscadorForm()

	monto = restaurante.plan.costo
	plan = restaurante.plan.nombre

	#Boton de pago
	if plan != 'Plata':
		boton = mercadopago(request, plan, int(monto))
	else:
		boton = ''
	ctx={
		'buscador':buscadorF,
		'boton_pago':boton,
		'restaurante':restaurante,
	}

	return render_to_response('administrador/perfil/plan.html', ctx, context_instance=RequestContext(request))


#View para cambiar la contrasena
@login_required
def perfil_modificar_password_view(request):
	form = modificarContrasenaForm(user=request.user)
	
	if request.method == "POST":
		form = modificarContrasenaForm(user=request.user, data=request.POST)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect('/administrador/perfil/')

	return HttpResponseRedirect('/administrador/perfil')


#View para mercadopago
def mercadopago(request, pago, monto, **kwargs):
	preference = {
	  "items": [
		{
		  "title": pago,
		  "quantity": 1,
		  "currency_id": "VEN",
		  "unit_price": monto
		}
	  ]
	}

	preferenceResult = mp.create_preference(preference)

	url = preferenceResult["response"]["init_point"]

	output = """
		<a href="{url}" name="MP-Checkout" class="blue-l-arall-rn">Pagar</a>
		<script type="text/javascript" src="http://mp-tools.mlstatic.com/buttons/render.js"></script>
	""".format (url=url)
	
	return output