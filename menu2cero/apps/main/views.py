# -*- coding: utf-8 -*-
# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.template.loader import get_template
from django.contrib.auth.models import User
from django.template import Context
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from menu2cero.apps.administrador.forms import *
from menu2cero.apps.administrador.views import loginUser
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from django.db.models import Q
from datetime import datetime, date
from models import *
from forms import *
from functions import *
from itertools import chain
from ipware.ip import get_real_ip


#Vista de pre-home y proximamente
def pre_home(request):


	ctx = {
		
	}

	return render_to_response('main/home/pre-home.html', ctx, context_instance=RequestContext(request))


#Vista del Home
@login_required
def index(request):
	userF = UserCreationForm()
	clienteF = ClienteForm()
	buscadorF = BuscadorForm()
	loginF = LoginForm()
	restaurantes_rec = []
	login = True
	registro = True
	restaurantes_destacados = []

	#Se veririca que se haya hecho un request a POST
	if request.POST:
		palabra = ''
		userF = UserCreationForm(request.POST)
		clienteF = ClienteForm(request.POST)
		buscadorF = BuscadorForm(request.POST)
		loginF = LoginForm(request.POST)

		#Caso para el buscador
		if buscadorF.is_valid():
			palabra = buscadorF.cleaned_data['palabra']
			return redirect('restaurantes', palabra=palabra)

		# Creando un nuevo usuario
		if userF.is_valid() and clienteF.is_valid():
			cliente = clienteF.save(commit=False)
			usuario = userF.save()
			cliente.user = usuario
			cliente.save()
			return HttpResponseRedirect('/')
		else:
			registro = False

		#Logueando al usuario
		if request.POST.get('email',False) and request.POST.get('password',False):
			login = loginUser(request)
			if login:
				return HttpResponseRedirect('/administrador/perfil/')

	#Restaurantes destacados
	restaurantes_diamante = Restaurante.objects.filter(plan__nombre='Diamante', visibilidad='Público', status='Activo')
	if restaurantes_diamante.count() != 0:
		restaurantes_diamante = restaurantes_diamante.random(6)
	restaurantes_platino = Restaurante.objects.filter(plan__nombre='Platino', visibilidad='Público', status='Activo')
	if restaurantes_platino.count() != 0:
		restaurantes_platino = restaurantes_platino.random(4)
	restaurantes_oro = Restaurante.objects.filter(plan__nombre='Oro', visibilidad='Público', status='Activo')
	if restaurantes_oro.count() != 0:
		restaurantes_oro = restaurantes_oro.random(2)
	restaurantes_destacados = list(chain(restaurantes_diamante,restaurantes_platino,restaurantes_oro))

	#Query para los restaurantes recientes
	restaurantes = Restaurante.objects.filter(visibilidad='Público', status='Activo').order_by('id')
	restaurantes = restaurantes.reverse()[:6]

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

		restaurantes_rec.append((restaurante,votacion))

	#Query para las categorias
	categorias = Categoria.objects.all()[:30]

	ctx = {
		'UserCreationForm': userF, 
		'ClienteForm': clienteF,
		'buscador': buscadorF, 
		'restaurantes_destacados': restaurantes_destacados,
		'restaurantes_rec': restaurantes_rec, 
		'categorias': categorias,
		'loginForm': loginF,
		'login':login,
		'registro':registro,
	}

	return render_to_response('main/home/home.html', ctx, context_instance=RequestContext(request))


#Vista de los restaurantes y el filtrador
@login_required
def restaurantes_view(request, palabra):

	i=0
	error = ''
	filtro = FiltroForm()
	userF = UserCreationForm()
	clienteF = ClienteForm()
	buscador = BuscadorForm()
	loginF = LoginForm()
	categorias_izq = []
	categorias_der = []
	restaurantes = []
	restaurantes_list = []
	servicios = []
	categorias = Categoria.objects.all().order_by('nombre')[:22]
	login = True
	registro = True

	# Categorias que se imprimen arriba del formulario filtrador
	for cat in categorias:
		i+=1
		if i >= 12:
			categorias_der.append(cat)
		else:
			categorias_izq.append(cat)

	#Informacion de los restaurantes
	if request.GET:
		filtro = FiltroForm(request.GET)
		buscadorF = BuscadorForm(request.GET)

		#Caso para el filtro de restaurantes
		if filtro.is_valid():
			cat = filtro.cleaned_data['Categorias']
			ciudad = filtro.cleaned_data['Ciudad']
			zona = filtro.cleaned_data['Zona']
			servicios = filtro.cleaned_data['Servicios']

			#Verificar que no todos los campos esten vacios
			if cat != None or ciudad != None or zona != None or servicios!=[]:

				#Verificacion de arreglo vacio
				if not servicios:
					servicios = None

				#Verificacion de string vacio
				#Extraccion del objeto de categoria
				try:
					cat = Categoria.objects.get(nombre__iexact=cat)
				except:
					cat = ''

				#Campos a buscar
				fields_list = []
				fields_list.append('categoria__id')
				fields_list.append('direccion__ciudad__nombre')
				fields_list.append('direccion__zona__nombre')
				fields_list.append('servicios__nombre')

				#Comparadores para buscar
				types_list=[]
				types_list.append('exact')
				types_list.append('exact')
				types_list.append('exact')
				types_list.append('in')

				#Valores a buscar
				values_list=[]
				if cat == '':
					values_list.append(None)
				else:
					values_list.append(cat.id)
				values_list.append(ciudad)
				values_list.append(zona)
				values_list.append(servicios)

				operator = 'and'

				restaurantes = dynamic_query(Restaurante, fields_list, types_list, values_list, operator).distinct()

			#Caso registro de cliente
			elif userF.is_valid() and clienteF.is_valid():
				return redirect('registro', formulario=userF)

			#Caso busqueda de palabra
			elif buscadorF.is_valid():
				palabra = buscadorF.cleaned_data['palabra']
				restaurantes = buscador_view(palabra)

			#Caso para el cual no se encontro ningun restaurante
			if restaurantes == []:
				restaurantes = Restaurante.objects.filter(visibilidad='Público',status='Activo').order_by('id').reverse()

	elif request.POST:
		userF = UserCreationForm(request.POST)
		clienteF = ClienteForm(request.POST)

		# Creando un nuevo usuario
		if userF.is_valid() and clienteF.is_valid():
			cliente = clienteF.save(commit=False)
			usuario = userF.save()
			cliente.user = usuario
			cliente.save()
			return HttpResponseRedirect('/')
		else:
			registro = False

		#Logueando al usuario
		if request.POST.get('email',False) and request.POST.get('password',False):
			login = loginUser(request)
			if login:
				return HttpResponseRedirect('/administrador/perfil/')

	#Caso para el cual la palabra tiene contenido
	elif palabra:

		restaurantes = buscador_view(palabra)
		#Caso en que se le dio click a una categoria
		try:
			#Caso en el que la categoria no esta vacia
			restaurantes = Restaurante.objects.filter(categoria__nombre__iexact=palabra, visibilidad='Público',status='Activo')
		except:
			error = 'Error'
	else:
		#Caso en el que no se introduce ninguna categoria especifica
		restaurantes = Restaurante.objects.filter(visibilidad='Público',status='Activo').order_by('id').reverse()

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

	#Busqueda de propiedades en el pais actual
	paginator = Paginator(restaurantes_list, 24)
	page = request.GET.get('page')

	try:
		restaurantes = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		restaurantes = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		restaurantes = paginator.page(paginator.num_pages)


	filtro = FiltroForm(request.GET)

	ctx = {
		'UserCreationForm': userF,
		'ClienteForm': clienteF,
		'buscador': buscador, 
		'filtro':filtro, 
		'restaurantes': restaurantes, 
		'categorias_der':categorias_der, 
		'categorias_izq': categorias_izq, 
		'servicios':servicios,
		'loginForm': loginF,
		'login':login,
		'registro':registro,
	}

	return render_to_response('main/restaurantes/restaurantes.html', ctx, context_instance=RequestContext(request))


#Vista del restaurante de cada restaurante
@login_required
def restaurante_view(request, restaurante):

	#Query para obtener los datos del restaurante.
	imagenes = []
	telefonos = []
	coord = []
	platos = []
	horarios = []
	dias = []
	direccion = ''
	lat = 0
	lng = 0		
	login = True
	registro = True
	desde = ''
	hasta = ''
	horaActual = ''

	#Conteo de views y verificacion de ingreso previo
	ip = get_real_ip(request)
	if ip is not None:
		# we have a real, public ip address for user
		print ip
	else:
		print 'ase'
		if request.session.test_cookie_worked():
			print ">>>> TEST COOKIE WORKED!"
			request.session.delete_test_cookie()

	#Formularios basicos
	buscadorF = BuscadorForm()
	userF = UserCreationForm()
	clienteF = ClienteForm()
	loginF = LoginForm()

	#Caso en el que el usuario realizo una busqueda
	if request.POST:
		buscadorF = BuscadorForm(request.POST)
		userF = UserCreationForm(request.POST)
		clienteF = ClienteForm(request.POST)

		#Caso para el buscador
		if buscadorF.is_valid():
			palabra = "buscar_"+buscador.cleaned_data['palabra']
			return redirect('restaurantes', palabra=palabra)


		# Creando un nuevo usuario
		if userF.is_valid() and clienteF.is_valid():
			cliente = clienteF.save(commit=False)
			usuario = userF.save()
			cliente.user = usuario
			cliente.save()
			return HttpResponseRedirect('/')
		else:
			registro = False

		#Logueando al usuario
		if request.POST.get('email',False) and request.POST.get('password',False):
			login = loginUser(request)
			if login:
				return HttpResponseRedirect('/administrador/perfil/')

	restaurante = get_object_or_404(Restaurante, slug=restaurante, status='Activo')

	#Preparacion del horario para mostrar
	horarios = Horario.objects.filter(restaurante=restaurante).order_by('id')
	# Fecha actual con hora y todo.
	fechaActual = datetime.now()
	# Enumera el dia actual, de 0 para lunes hasta 6 para domingo.
	numeroDiaActual = fechaActual.weekday()
	diasSemana = {0:"Lunes",
				1:"Martes",
				2:"Miércoles",
				3:"Jueves",
				4:"Viernes",
				5:"Sábado",
				6:"Domingo"}
	disponible = False

	for horario in horarios:
		# Verifica si el restaurante esta en el horario de abierto.
		if diasSemana[numeroDiaActual] == horario.dia:
			# Horas desde y hasta y la hora actual
			desde = datetime.strptime(horario.desde, "%I:%M %p").time()
			hasta = datetime.strptime(horario.hasta, "%I:%M %p").time()
			horaActual = fechaActual.time()
			# Si esta dentro del horario estara abierto.
			if horaActual >= desde and horaActual <= hasta:
				disponible = True
			else:
				disponible = False

		dias.append((horario.dia, horario.desde + ' a ' + horario.hasta))
	horaActual = fechaActual.time()
	horario = horario_restaurante(dias)

	#Imagenes del restaurante
	try:
		imagenes = Imagen.objects.filter(restaurante=restaurante)
	except:
		error = 'Este rest no posee imagenes'

	#Votos para los restaurantes
	votos = Voto.objects.filter(restaurante=restaurante)
	puntos = 0

	for voto in votos:
		puntos = puntos + voto.valor

	#Calculo de puntos
	cantidad = len(votos)
	try:
		puntos = puntos/cantidad
	except:
		error = 'Division por cero!'

	#Redes sociales del restaurante
	try:
		redes = Red_social.objects.get(restaurante=restaurante)
	except:
		redes = Red_social(facebook='', twitter='', instagram='')

	#Direccion del restaurante y otros datos.
	direccion = restaurante.direccion
	lat = direccion.latitud
	lng = direccion.longitud
	direccion = direccion.direccion + '. ' + direccion.zona.nombre + ', ' + direccion.ciudad.nombre

	try:
		telefonos = TelefonoRestaurante.objects.filter(restaurante=restaurante)
	except:
		telefonos = 'Este rest no posee telefonos'

	#Informacion de los metodos de pago del restaurante.
	metodos = Metodo.objects.all()

	#Servicios que existen
	servicios = Servicio.objects.all()

	#Seccion del menu y sus platos
	try:
		menu = Menu.objects.get(restaurante=restaurante)
		platos = Plato.objects.filter(menu=menu).order_by('tipo')
	except:
		error = 'Este restaurante no posee menus'

	#Tipos posibles de platos
	tipos = []
	contador = []
	j = 0
	i = 1

	#Preparado los platos por tipo de plato
	for plato in platos:
		if plato.tipo not in tipos:
			contador.insert(j,i)
			tipos.append(plato.tipo)
			i=1
			j=j+1
		#Aca entra en el caso en que el plato esta repetido
		elif plato.tipo in tipos:
			i=i+1

	#Cantidad de platos que hay de cada tipo
	contador.insert(j,i)
	contador.pop(0)

	#Tuplas con la informacion de cantidad y tipo de plato
	arreglo = []
	i=0
	for tipo in tipos:
		arreglo.append((tipo, contador[i], tipo.id))
		i = i+1

	ctx = {
		'UserCreationForm': userF,
		'ClienteForm': clienteF,
		'buscador': buscadorF,
		'loginForm': loginF,
		'restaurante': restaurante,
		'categorias': restaurante.categoria,
		'imagenes':imagenes,
		'puntos': puntos,
		'redes':redes,
		'horario':horario,
		'votos':cantidad,
		'lat': lat,
		'lng': lng,
		'plan': restaurante.plan, 
		'servicios_rest': restaurante.servicios.all, 
		'servicios': servicios, 
		'metodos_rest': restaurante.metodos_pago.all, 
		'metodos': metodos, 
		'telefonos': telefonos,
		'disponible': disponible, 
		'platos': platos, 
		'arreglo': arreglo,
		'login':login,
		'registro':registro,
	}

	return render_to_response('main/restaurante/restaurante.html', ctx, context_instance=RequestContext(request))


#Vista para contactar a la compania
@login_required
def contactos_view(request):

	#Formularios basicos
	buscadorF = BuscadorForm()
	userF = UserCreationForm()
	clienteF = ClienteForm()
	loginF = LoginForm()
	contactF = ContactForm()

	if request.POST:
		userF = UserCreationForm(request.POST)
		clienteF = ClienteForm(request.POST)
		contactF = ContactForm(request.POST)

		# Creando un nuevo usuario
		if userF.is_valid() and clienteF.is_valid():
			cliente = clienteF.save(commit=False)
			usuario = userF.save()
			cliente.user = usuario
			cliente.save()
			return HttpResponseRedirect('/')

		# Envio de correo de contacto
		if contactF.is_valid():
			envio = contact_email(request, contactF)
			contactoF = ContactForm()

	ctx = {
		'UserCreationForm': userF,
		'ClienteForm': clienteF,
		'buscador': buscadorF,
		'loginForm': loginF,
		'ContactForm': contactF,
	}

	return render_to_response('main/contactos/contactos.html', ctx, context_instance=RequestContext(request))


#Creador de horario para mostrar en el restaurante
def horario_restaurante(dias):

	# Agrupa los dias consecutivos repetidos.
	i = 0
	j = 0
	horario = ''
	# Arreglo de grupo de dias, maximo 7 que es el caso en que todos los dias son diferentes
	agrupados = [[],[],[],[],[],[],[]]

	# Verifica que dias son consecutivamente iguales y los coloca en el arreglo de agrupados.
	while i < len(dias):
		# Inicializa el comparador y agrega el lunes a agrupados.
		if i == 0:
			comparador = dias[i]
			agrupados[j].append(comparador)
			i += 1
			continue

		# Si el dia es igual al comparador, se agrega el dia a agrupados,
		# en caso contrario se actualiza el comparador al dia actual y
		# se agrega a agrupados en una nueva pocision.
		if comparador[1] == dias[i][1]:
			agrupados[j].append(dias[i])
			i += 1
		else:
			comparador = dias[i]
			j += 1
			agrupados[j].append(dias[i])
			i += 1

	# Construye el resultado final depende de cuantos dias haya en un determinado grupo.
	for grupo in agrupados:
		aux = len(grupo)
		# Si hay 3 dias o mas en un grupo.
		if aux >= 3:
			horario += grupo[0][0] + " a " + grupo[aux-1][0] + " de " + grupo[0][1] + ". "
		# Si hay exactamente 2 es otro tipo de horario.
		elif aux == 2:
			horario += grupo[0][0] + " y " + grupo[1][0] + " de " + grupo[0][1] + ". "
		else:
			for g in grupo:
				horario += g[0] + " " + g[1] + ". "

	return horario


#View de la barra de busqueda superior
def buscador_view(palabra):

	error = ''
	try:
		restaurantes = Restaurante.objects.filter(nombre__icontains=palabra, visibilidad='Público',status='Activo')
	except:
		error = 'No se encontraron coincidencias'

	#Caso para los restaurantes de una categoria especifica
	if not restaurantes:
		try:
			restaurantes = Restaurante.objects.filter(categoria__nombre__icontains=palabra, visibilidad='Público',status='Activo')
		except:
			error = 'No se encontraron coincidencias'

	#Caso para los restaurantes con un plato especifico
	if not restaurantes:
		try:
			#NOTA: Falta que funcione
			print 'Platos'
			restaurantes = Restaurantes.objects.filter(menu__plato__nombre__icontains=palabra, visibilidad='Público',status='Activo')
		except:
			error = 'No se encontraron coincidencias'

	#Caso para los restaurantes con ciudades especificas		
	if not restaurantes:
		try:
			restaurantes = Restaurante.objects.filter(direccion__ciudad__nombre__icontains=palabra, visibilidad='Público',status='Activo')
		except:
			error = 'No se encontraron coincidencias'

	#Caso para los restaurantes con descripciones especificas
	if not restaurantes:
		try:
			restaurantes = Restaurante.objects.filter(descripcion__icontains=palabra, visibilidad='Público',status='Activo')
		except:
			error = 'No se encontraron coincidencias'

	return restaurantes


#View para las votaciones de cada restaurante
def votacion_view(request):

	rest_id = request.GET['restaurante_id']
	valor = request.GET['valor']

	#Se verifica que se recibio el id y el valor
	if rest_id and valor:
		restaurante = Restaurante.objects.get(id=int(rest_id))
		voto = Voto(valor=valor)
		voto.save()
		restaurante.votos.add(voto)

	return HttpResponse(True)


#Query dinamico extraido de un proyecto ajeno
def dynamic_query(model, fields, types, values, operator):
	"""
	 Takes arguments & constructs Qs for filter()
	 We make sure we don't construct empty filters that would
		return too many results
	 We return an empty dict if we have no filters so we can
		still return an empty response from the view
	"""
	
	queries = []
	for (f, t, v) in zip(fields, types, values):

		if v != None:
			if t == 'in':
				kwargs = {str('%s__%s' % (f,t)) : v}
			else:
				kwargs = {str('%s__%s' % (f,t)) : str('%s' % v)}
			queries.append(Q(**kwargs))
	
	# Make sure we have a list of filters
	if len(queries) > 0:
		q = Q()
		# AND/OR awareness
		for query in queries:
			if operator == "and":
				q = q & query
			elif operator == "or":
				q = q | query
			else:
				q = None
		if q:
			# We have a Q object, return the QuerySet
			return model.objects.filter(q)
	else:
		# Return an empty result
		return {}