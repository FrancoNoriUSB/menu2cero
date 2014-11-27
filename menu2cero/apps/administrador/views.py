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

#Vista para el ingreso de los usuarios.
def admin_login_view(request):

	username = ''
	password = ''
	
	#Formularios basicos
	buscadorF = BuscadorForm()
	loginF = LoginForm()

	if request.user.is_authenticated() and request.user:
		
		return HttpResponseRedirect('/administrador/perfil')

	if request.method == "POST":

		#Caso para el buscador
		if buscadorF.is_valid():

			filtro = FiltroForm(request.POST)
			palabra = "buscar_"+buscador.cleaned_data['palabra']
			return redirect('restaurantes', palabra=palabra)

		loginF = LoginForm(request.POST)
		username = request.POST['username']
		password = request.POST['password']
		usuario = authenticate(username=username, password=password)

		if usuario:
	            # Caso del usuario activo
	            if usuario.is_active:
	                login(request, usuario)
	                return HttpResponseRedirect('/administrador/perfil')
	            else:
	                return "Tu cuenta esta bloqueada"
		else:
		    # Usuario invalido o no existe!
		    print "Invalid login details: {0}, {1}".format(username, password)

	ctx = {
		'buscador':buscadorF, 
		'login': loginF
	}
	return render_to_response('administrador/login/login.html', ctx, context_instance=RequestContext(request))

#Vista del perfil del usuario logueado
@login_required
def admin_perfil_view(request):

	#Variables y Formularios
	cliente = get_object_or_404(Cliente, user=request.user)
	buscadorF = BuscadorForm()
	eliminarF = EliminarForm()
	logosF = LogosForm()
	registroF = RegistroForm(instance=cliente.user, initial={
		'nombre_de_usuario':cliente.user.username,
		'cargo':cliente.cargo,
		'rif':cliente.rif})
	modificarF = modificarContrasenaForm(user=cliente.user)
	restaurantes = []
	error = ''
	vencidos = []

	#Caso para el buscador
	if request.method == 'POST':
		buscadorF = BuscadorForm(request.POST)
		modificarF = modificarContrasenaForm(request.POST)
		registroF = RegistroForm(request.POST, instance=cliente.user)

		if buscadorF.is_valid():
			filtro = FiltroForm(request.POST)
			palabra = "buscar_"+buscador.cleaned_data['palabra']
			return redirect('restaurantes', palabra=palabra)

		elif modificarF.is_valid():
			modificarF.save()

		elif registroF.is_valid():
			cargo = registroF.cleaned_data['cargo']
			Cliente.objects.filter(user=request.user).update(cargo=cargo)
			registroF.save()

	usuario = request.user

	#Restaurantes del cliente logueado
	try:
		restaurantes = Restaurante.objects.filter(cliente__user_id=usuario.id).exclude(status='Eliminado')
	except:
		error = 'Cliente no posee restaurantes'

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
		'RegistroForm':registroF,
		'modificarContrasenaForm': modificarF,
		'restaurantes':restaurantes, 
		'cliente': cliente, 
		'vencidos': vencidos, 
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
	info_principal = PrincipalForm()
	horarios_form = HorariosForm()
	direccionF = DireccionForm()

	#Telefonos del restaurante
	telefonoFormSet = inlineformset_factory(Restaurante, TelefonoRestaurante, TelefonoRestauranteForm, can_delete=False, extra=1)
	telefonoF = telefonoFormSet()

	#Formularios otra informacion
	descripcion = DescripcionForm()
	redes_sociales = RedesForm()

	#Formularios de imagenes
	logosF = LogosForm()
	imagenF = ImagenForm()

	ctx = {
		'buscador':buscadorF,
		'PrincipalForm':info_principal,
		'HorariosForm':horarios_form,
		'DireccionForm':direccionF,
		'TelefonoRestauranteForm': telefonoF,
		'DescripcionForm': descripcion,
		'RedesForm': redes_sociales,
		'LogosForm': logosF,
		'ImagenForm':imagenF,
		'lat':lat,
		'lng':lng,
	}

	return render_to_response('administrador/agregar/agregar.html', ctx, context_instance=RequestContext(request))

#View de la edicion del restaurante (simplemente inicializa la vista)
@login_required
def admin_editar_restaurante_view(request, id_rest):

	#Declaracion de variables
	buscadorF = BuscadorForm()
	vencidos = []
	pago = []
	restaurante = []
	categorias_rest = []
	servicios_rest = []
	metodos_rest = []
	platos_data = []
	red_social = Red_social(facebook='', twitter='')
	puntuacion = 0

	#Variables para horarios
	horarios = []
	dataHorarios = []

	#Verificacion de que el restaurante pertenece al usuario
	restaurante = get_object_or_404(Restaurante, cliente__user_id=request.user.id, id=id_rest)

	#Coordenadas del restaurante
	coord = str(restaurante.direccion.coord).split(',')
	lat = coord[0]
	lng = coord[1]
	coord = restaurante.direccion.coord

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

	#Telefonos del restaurante
	telefonoFormSet = inlineformset_factory(Restaurante, TelefonoRestaurante, TelefonoRestauranteForm, can_delete=False, extra=0)
	telefonoF = telefonoFormSet(instance=restaurante)

	#Manejo de info para el horario del restaurante
	horarios = Horario.objects.filter(restaurante=restaurante)

	for horario in horarios:
		dataHorarios.append((horario.desde, horario.hasta))

	info_principal = PrincipalForm(instance=restaurante)

	categorias = Categoria.objects.filter(restaurante=restaurante)

	for categoria in categorias:
		categorias_rest.append(str(categoria.id).decode('unicode-escape'))

	horarios_form = HorariosForm(initial={
		'lunes_desde':dataHorarios[0][0], 'lunes_hasta':dataHorarios[0][1], 
		'martes_desde':dataHorarios[1][0],'martes_hasta':dataHorarios[1][1], 
		'miercoles_desde':dataHorarios[2][0], 'miercoles_hasta':dataHorarios[2][1], 
		'jueves_desde':dataHorarios[3][0], 'jueves_hasta':dataHorarios[3][1], 
		'viernes_desde':dataHorarios[4][0], 'viernes_hasta':dataHorarios[4][1], 
		'sabado_desde':dataHorarios[5][0], 'sabado_hasta':dataHorarios[5][1],
		'domingo_desde':dataHorarios[6][0], 'domingo_hasta':dataHorarios[6][1]
	})

	direccionF = DireccionForm(instance=restaurante.direccion)

	#Inicializacion de los formularios de Otra Informacion
	servicios = Servicio.objects.filter(restaurante=restaurante)

	for servicio in servicios:
		servicios_rest.append(str(servicio.id).decode('unicode-escape'))

	metodos = Metodo.objects.filter(restaurante=restaurante)

	for metodo in metodos:
		metodos_rest.append(str(metodo.id).decode('unicode-escape'))

	descripcion = DescripcionForm(initial={'descripcion_rest': restaurante.descripcion, 'servicios': servicios_rest, 'metodos_de_pago': metodos_rest})

	try:
		red_social = Red_social.objects.get(restaurante=id_rest)
	except:
		error = 'Este restaurante no posee red social'

	#Redes sociales del restaurante
	redes_sociales = RedesForm(instance=red_social)

	#Logo del restaurante
	logoRestF = logoRestForm(instance=restaurante)

	#Inicializacion de los formularios de imagenes
	logosF = LogosForm()

	#Inicializacion del formulario de imagenes de resturante
	imagenes = Imagen.objects.filter(restaurante=restaurante)
	imagenFormSet = inlineformset_factory(Restaurante, Imagen, form =  ImagenForm, extra = 1, can_delete=False)
	imagenF = imagenFormSet(instance=restaurante, queryset=Imagen.objects.filter(restaurante=restaurante))

	#Inicializacion de los formularios del menu
	platos = Plato.objects.filter(menu__restaurante=restaurante)
	platosFormSet = inlineformset_factory(Menu, Plato, form = PlatosForm, extra = 1, can_delete=False)
	try:
		menu = Menu.objects.get(restaurante=restaurante)
	except:
		menu = Menu()
	platosF = platosFormSet(instance=menu, queryset=Plato.objects.filter(menu__restaurante=restaurante))

	ctx = {
		'buscador':buscadorF,
		'PrincipalForm':info_principal, 
		'HorariosForm':horarios_form,
		'DireccionForm':direccionF,
		'TelefonoRestauranteForm': telefonoF, 
		'DescripcionForm': descripcion,
		'RedesForm': redes_sociales, 
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
		'logo':restaurante.logo,
	}

	return render_to_response('administrador/editar/editar.html', ctx, context_instance=RequestContext(request))

#Vista para el manejo (guardado) del formulario info basica del restaurante
@login_required
def restaurante_info_basica(request, id_rest):

	#Inicializacion de variables
	categorias_rest = []
	existe = True
	dias = []

	try:
		restaurante = Restaurante.objects.get(cliente__user_id=request.user.id, id=id_rest)
	except:
		restaurante = []

	#Caso en que se edita un restaurante
	if request.POST and restaurante != []:
		principalF = PrincipalForm(request.POST, instance = restaurante)
		horariosF = HorariosForm(request.POST)
		direccionF = DireccionForm(request.POST, instance = restaurante.direccion)
		telefonoFormSet = inlineformset_factory(Restaurante, TelefonoRestaurante, form = TelefonoRestauranteForm, can_delete=False)
		telefonoF = telefonoFormSet(request.POST, instance=restaurante, queryset=restaurante.telefonos.all())

		#Verificacion de que los campos de los formularios se llenaron
		if principalF.is_valid() and horariosF.is_valid() and direccionF.is_valid() and telefonoF.is_valid():

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
			telefonoF.save()

			#Manejo del formulario de direcciones
			direccion = direccionF.save(commit=False)
			direccion.restaurante = restaurante
			direccion.save()

		return HttpResponseRedirect('/administrador/editar/'+str(id_rest))

	#Caso en el que se agrega un restaurante
	elif request.POST and restaurante == []:

		principalF = PrincipalForm(request.POST)
		horariosF = HorariosForm(request.POST)
		direccionF = DireccionForm(request.POST)
		telefonoFormSet = inlineformset_factory(Restaurante, TelefonoRestaurante, form = TelefonoRestauranteForm, can_delete=False)
		telefonoF = telefonoFormSet(request.POST)

		#Verificacion de que los campos de los formularios se llenaron
		if principalF.is_valid() and horariosF.is_valid() and direccionF.is_valid() and telefonoF.is_valid():

			categorias = principalF.cleaned_data['categoria']

			#Datos del restaurante
			restaurante = principalF.save(commit=False)
			restaurante.descripcion = u'<Este restaurante no posee descripción en estos momentos.>'
			restaurante.status = 'Inactivo'
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

			return HttpResponseRedirect('/administrador/editar/'+str(id_rest))

	return HttpResponseRedirect('/administrador/agregar/')

#Vista para el manejo (guardado) del formulario otra info del restaurante
@login_required
def restaurante_otra_info(request, id_rest):

	#Inicializacion de variables
	modifico = False

	restaurante = get_object_or_404(Restaurante, id=id_rest)
	try:
		redes = Red_social.objects.get(restaurante=restaurante)
	except:
		redes = []

	#Caso en que se postea el formulario
	if request.POST:
		descripcionF = DescripcionForm(request.POST)

		#Caso en el que el restaurante no tiene redes
		if redes != []:
			redesF = RedesForm(request.POST, instance = redes)
		else:
			redesF = RedesForm(request.POST)

		#Verificacion de los formularios
		if descripcionF.is_valid() and redesF.is_valid():
			restaurante.descripcion=descripcionF.cleaned_data['descripcion_rest']
			restaurante.servicios=descripcionF.cleaned_data['servicios']
			restaurante.metodos_pago=descripcionF.cleaned_data['metodos_de_pago']
			restaurante.save()

			#Caso en el que la red ya existe
			if redes != []:
				redesF.save()

			#Caso en el que no existe red aun
			else:
				redes = redesF.save(commit=False)
				redes.restaurante = restaurante
				redes.save()

	return HttpResponseRedirect('/administrador/editar/'+id_rest)

#Vista para el manejo (guardado) del formulario de imagenes del restaurante
@login_required
def restaurante_imagenes(request, id_rest):

	#Inicializacion de variables
	modifico = False

	restaurante = get_object_or_404(Restaurante, id=id_rest)
	imagenes = Imagen.objects.filter(restaurante=restaurante)

	#Caso en que se postea el formulario
	if request.POST:
		logoRestF = logoRestForm(request.POST, request.FILES, instance=restaurante)
		logosF = LogosForm(request.POST)
		imagenesFormSet = inlineformset_factory(Restaurante, Imagen, form =  ImagenForm, can_delete=False)
		imagenesF = imagenesFormSet(request.POST, request.FILES, instance=restaurante,  queryset=Imagen.objects.filter(restaurante=restaurante))

		#Caso en el que se selecciono un logo de los que se disponen
		if logosF.is_valid():
			logo = logosF.cleaned_data['logos']
			Restaurante.objects.filter(id=restaurante.id).update(logo="files/img/"+str(logo)+".jpg")
		
		#Caso en el que el rest agrego un logo en el formulario de logoRestF
		elif logoRestF.is_valid():
			logoRestF.save()
		
		#Caso en el que se agregaron imagenes al rest
		if imagenesF.is_valid():
			imagenesF.save()

	return HttpResponseRedirect('/administrador/editar/'+str(id_rest))

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

	if restaurante.abierto == True:
		restaurante.abierto = False
		restaurante.save()
	else:
		restaurante.abierto = True
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

#View para cambiar la contrasena
@login_required
def perfil_modificar_password_view(request):
	form = modificarContrasenaForm(user=request.user)
	
	if request.method == "POST":
		form = modificarContrasenaForm(user=request.user, data=request.POST)
		if form.is_valid():
			form.save()
			print 'Modifico!'
			return HttpResponseRedirect('/administrador/perfil/')
	else:
		form = modificarContrasenaForm(user=request.user)

	return HttpResponseRedirect('/administrador/perfil')