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
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from django.db.models import Q
from datetime import datetime, date
from models import *
from forms import *
from functions import *


#Vista del Home
def index(request):
	userF = UserCreationForm()
	clienteF = ClienteForm()
	buscadorF = BuscadorForm()
	loginF = LoginForm()

	#Se veririca que se haya hecho un request a POST
	if request.POST:
		palabra = ''
		userF = UserCreationForm(request.POST)
		clienteF = ClienteForm(request.POST)
		buscadorF = BuscadorForm(request.POST)

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

	#Query para los restaurantes destacados
	restaurantes_dest = Restaurante.objects.filter(plan__nombre='Azul', visibilidad='Público', status='Activo').order_by('?')[:12]
	
	#Query para los restaurantes recientes
	restaurantes_rec = Restaurante.objects.filter(visibilidad='Público', status='Activo').order_by('id')
	restaurantes_rec = restaurantes_rec.reverse()[:6]
	
	#Query para las categorias
	categorias = Categoria.objects.all()[:30]

	ctx = {
		'UserCreationForm': userF, 
		'ClienteForm': clienteF,
		'buscador': buscadorF, 
		'restaurantes_dest': restaurantes_dest,
		'restaurantes_rec': restaurantes_rec, 
		'categorias': categorias,
    	'loginForm': loginF
	 }
	return render_to_response('main/home/home.html', ctx, context_instance=RequestContext(request))


#Vista de los restaurantes y el filtrador
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
	servicios = []
	categorias = Categoria.objects.all().order_by('nombre')[:22]

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
			tipo = filtro.cleaned_data['Tipo']
			servicios = filtro.cleaned_data['Servicios']

			#Verificar que no todos los campos esten vacios
			if cat != None or ciudad != None or zona != None or tipo != '' or servicios!=[]:

				#Verificacion de arreglo vacio
				if not servicios:
					servicios = None

				#Verificacion de string vacio
				if tipo == '':
					tipo = None

				#Extraccion del objeto de categoria
				try:
					cat = Categoria.objects.get(nombre=cat)
				except:
					cat = ''

				#Campos a buscar
				fields_list = []
				fields_list.append('categoria')
				fields_list.append('direccion__ciudad')
				fields_list.append('direccion__zona')
				fields_list.append('tipo')
				fields_list.append('servicios')

				#Comparadores para buscar
				types_list=[]
				types_list.append('id__exact')
				types_list.append('nombre__exact')
				types_list.append('nombre__exact')
				types_list.append('exact')
				types_list.append('nombre__in')

				#Valores a buscar
				values_list=[]
				if cat == '':
					values_list.append(None)
				else:
					values_list.append(cat.id)
				values_list.append(ciudad)
				values_list.append(zona)
				values_list.append(tipo)
				values_list.append(servicios)

				operator = 'and'

				restaurantes = dynamic_query(Restaurante, fields_list, types_list, values_list, operator)

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

	#Caso para el cual la palabra tiene contenido
	elif palabra:

		restaurantes = buscador_view(palabra)
		#Caso en que se le dio click a una categoria
		try:
			#Caso en el que la categoria no esta vacia
			restaurantes = Restaurante.objects.filter(categoria__nombre=palabra, visibilidad='Público',status='Activo')
		except:
			error = 'Error'
	else:
		#Caso en el que no se introduce ninguna categoria especifica
		restaurantes = Restaurante.objects.filter(visibilidad='Público',status='Activo').order_by('id').reverse()

	#Busqueda de propiedades en el pais actual
	paginator = Paginator(restaurantes, 24)
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
        'loginForm': loginF
	}
	return render_to_response('main/restaurantes/restaurantes.html', ctx, context_instance=RequestContext(request))


#Vista del perfil de cada restaurante
def perfil_view(request, id_rest, restaurante):

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

	restaurante = get_object_or_404(Restaurante, id=id_rest)

	#Preparacion del horario para mostrar
	horarios = Horario.objects.filter(restaurante=restaurante)

	for horario in horarios:
		dias.append((horario.dia, horario.desde + ' a ' + horario.hasta))

	horario = horario_restaurante(dias)

	#Imagenes del restaurante
	try:
		imagenes = Imagen.objects.filter(restaurante=restaurante)
	except:
		error = 'Este rest no posee imagenes'

	#Direccion del restaurante y otros datos.
	direccion = restaurante.direccion
	coord = str(direccion.coord).split(',')
	lat = coord[0]
	lng = coord[1]
	direccion = direccion.direccion + '. ' + direccion.zona.nombre + ', ' + direccion.ciudad.nombre

	try:
		telefonos = TelefonoRestaurante.objects.filter(restaurante=restaurante)
	except:
		telefonos = 'Este rest no posee telefonos'

	#Rango de la cantidad de imagenes.
	rango_img =[]
	for i in range(len(imagenes)):
 		rango_img.append(i)

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

	ctx = {
		'UserCreationForm': userF,
		'ClienteForm': clienteF,
		'buscador': buscadorF,
        'loginForm': loginF,
		'restaurante': restaurante,
		'categorias': restaurante.categoria,
		'rango_img': rango_img,
		'puntos': puntos,
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
		'disponible': restaurante.abierto, 
		'platos': platos, 
		'arreglo': arreglo
	}
	return render_to_response('main/perfil/perfil.html', ctx, context_instance=RequestContext(request))


#Vista para contactar a la compania
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


#Creador de horario para mostrar en el perfil
def horario_restaurante(dias):

	i=0
	horario = ''
	dia_ini = ''
	dia_fin = ''

	#Algoritmo para la creacion del string del horario
	for dia in dias:
		#Caso inicial del primer dia
		if dia[0] == "Lunes":
			dia_ini = dia
			dia_fin = dia
		else:

			#Si el dia que estoy revisando, es igual al inicial, entonces sigo y mantengo los dias
			if dia_ini[1] == dia[1]:
				dia_fin = dia

				#Caso en el que es el mismo horario todos los dias
				if i==6:
					horario = dia_ini[0] + ' a ' + dia_fin[0] + ' de ' + dia_ini[1] + '.'	
			else:

				#Caso que no es el ultimo dia a revisar
				if i != 6:

					#Caso para los cuales dos dias consecutivos tienen horarios distintos
					if dia_ini == dia_fin:
						horario = horario + dia_ini[0] + ' de ' + dia_ini[1] + ', '
						dia_ini = dia
						dia_fin = dia

					#Caso para el cual los dias consecutivos son distintos
					else:
						horario = horario + dia_ini[0] + ' a ' + dia_fin[0] + ' de ' + dia_ini[1] + ', '
						dia_ini = dia
						dia_fin = dia

				else:
					#Caso que llego al Domingo y comparara
					if dia_ini == dia_fin:
						horario = horario + dia_ini[0] + ' de ' + dia_ini[1]
						horario = horario + dia_fin[0] + ' de ' + dia_ini[1] + '.'
					else:
						horario = horario + dia_ini[0] + ' a ' + dia_fin[0] + ' de ' + dia_ini[1] + '.'	

		i+=1
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
        # We only want to build a Q with a value
        if v != None:
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
            print q
            return model.objects.filter(q)
    else:
        # Return an empty result
        return {}