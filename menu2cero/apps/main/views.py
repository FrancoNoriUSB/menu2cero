# -*- coding: utf-8 -*-
# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.template.loader import get_template
from django.template import Context
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from models import *
from forms import *
from django.db.models import Count
from django.db.models import Q
from datetime import datetime, date


#Vista del Home
def index(request):
	correo = ""
	registro = RegistroForm(request.POST)
	buscador = BuscadorForm(request.POST)
	#Se veririca que se haya hecho un request a POST
	if request.method == "POST" and (registro.is_valid() or buscador.is_valid()):
		palabra = ''
		registro = RegistroForm(request.POST)
		buscador = BuscadorForm(request.POST)
		#Se verifica que los datos del formulario sean correctos y que no exista el cliente
		if registro.is_valid():
			correo = registro.cleaned_data['correo']
			existe = Cliente.objects.filter(correo=correo)

			if not existe:
				#Se guarda el formulario
				registro.save()
				#Se crea el contexto a enviar
				info = "Cliente registrado con éxito!"
				ctx = {'info': info, 'buscador': buscador, 'registro': registro}
				return render_to_response('home/home.html', ctx, context_instance=RequestContext(request))
			else:
				#Se realizan las operaciones para el caso en el 
				#que el cliente ya existe
				info = "Cliente ya existente!\n Registre un correo distinto!"
				ctx = {'info': info, 'registro': registro, 'buscador': buscador}
				return render_to_response('home/home.html', ctx, context_instance=RequestContext(request))

		#Caso para el buscador
		elif buscador.is_valid():

			filtro = FiltroForm(request.POST)
			palabra = "buscar_"+buscador.cleaned_data['palabra']
			return redirect('restaurantes', palabra=palabra)

		# else:
		# 	ctx = {'registro': registro, 'buscador': buscador}
		# 	return render_to_response('home/home.html', ctx, context_instance=RequestContext(request))
		
	else:
		#Query para los restaurantes destacados
		restaurantes_dest = Restaurante.objects.filter(plan__nombre='Azul', visibilidad='Público',status='Activo').order_by('?')[:12]
		
		#Query para los restaurantes recientes
		restaurantes_rec = Restaurante.objects.filter(visibilidad='Público',status='Activo').order_by('id')
		restaurantes_rec = restaurantes_rec.reverse()[:6]
		
		#Query para las categorias
		categorias = Categoria.objects.all()[:30]

		buscador = BuscadorForm(request.POST)
		registro = RegistroForm(request.POST)
		ctx = {
			'registro': registro, 
			'buscador': buscador, 
			'restaurantes_dest': restaurantes_dest,
			 'restaurantes_rec': restaurantes_rec, 
			 'categorias': categorias
		 }
		return render_to_response('home/home.html', ctx, context_instance=RequestContext(request))


#Vista de los restaurantes y el filtrador
def restaurantes_view(request, palabra):

	filtro = FiltroForm()
	buscador = BuscadorForm()
	error = ''
	servicios = []
	categorias = Categoria.objects.all().order_by('nombre')[:22]
	categorias_izq = []
	categorias_der = []
	restaurantes = []

	# Categorias que se imprimen arriba del formulario filtrador
	i=0
	for cat in categorias:
		i+=1
		if i >= 12:
			categorias_der.append(cat)
		else:
			categorias_izq.append(cat)

	#Informacion de los restaurantes
	if request.POST:

		filtro = FiltroForm(request.POST)
		buscador = BuscadorForm(request.POST)

		if filtro.is_valid():

			#Caso para el buscador
			if buscador.is_valid():
				palabra = buscador.cleaned_data['palabra']
				restaurantes = buscador_view(palabra)
			else:
				cat = filtro.cleaned_data['Categorias']
				ciudad = filtro.cleaned_data['Ciudad']
				zona = filtro.cleaned_data['Zona']
				tipo = filtro.cleaned_data['Tipo']
				servicios = filtro.cleaned_data['Servicios']

				if not servicios:
					servicios = None

				if tipo == '':
					tipo = None

				cat = Categoria.objects.get(nombre=cat)

				fields_list = []
				fields_list.append('categoria')
				fields_list.append('direccion')
				fields_list.append('direccion')
				fields_list.append('tipo')
				fields_list.append('servicios')

				types_list=[]
				types_list.append('id__exact')
				types_list.append('ciudad__exact')
				types_list.append('zona__exact')
				types_list.append('exact')
				types_list.append('nombre__in')

				values_list=[]
				values_list.append(cat.id)
				values_list.append(ciudad)
				values_list.append(zona)
				values_list.append(tipo)
				values_list.append(servicios)

				operator = 'and'
			
				restaurantes = dynamic_query(Restaurante, fields_list, types_list, values_list, operator)
		
			#Caso para el cual no se encontro ningun restaurante
			if restaurantes == []:
				restaurantes = Restaurante.objects.filter(visibilidad='Público',status='Activo').order_by('id').reverse()

	#Caso para el cual la palabra tiene contenido
	elif palabra:

		#Caso en el que la palabra tiene el predicado de busqueda
		if palabra.startswith('buscar_'):
			palabra = palabra.lstrip('buscar_')
			restaurantes = buscador_view(palabra)
		else:	
			#Caso en que se le dio click a una categoria
			try:
				#Caso en el que la categoria no esta vacia
				restaurantes = Restaurante.objects.filter(categoria__nombre=palabra)
			except:
				error = 'Error'

	else:
		#Caso en el que no se introduce ninguna categoria especifica
		restaurantes = Restaurante.objects.filter(visibilidad='Público',status='Activo').order_by('id').reverse()

	filtro = FiltroForm(request.POST)

	ctx = {
		'buscador': buscador, 
		'filtro':filtro, 
		'restaurantes': restaurantes, 
		'categorias_der':categorias_der, 
		'categorias_izq': categorias_izq, 
		'servicios':servicios
	}
	return render_to_response('restaurantes/restaurantes.html', ctx, context_instance=RequestContext(request))


#Vista del perfil de cada restaurante
def perfil_view(request, id_rest):

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
	buscador = BuscadorForm(request.POST)
	registro = RegistroForm(request.POST)

	#Caso en el que el usuario realizo una busqueda
	if request.method == "POST":

		#Caso para el buscador
		if buscador.is_valid():

			filtro = FiltroForm(request.POST)
			palabra = "buscar_"+buscador.cleaned_data['palabra']
			return redirect('restaurantes', palabra=palabra)

	restaurante = get_object_or_404(Restaurante, id=id_rest)
	logo = restaurante.logo
	categorias = restaurante.categoria
	descripcion = restaurante.descripcion
	disponible = restaurante.abierto
	metodos_rest = restaurante.metodos_pago.all()
	servicios_rest = restaurante.servicios.all()

	#Preparacion del horario para mostrar
	horarios = Horario.objects.filter(restaurante=restaurante)

	for horario in horarios:
		dias.append((horario.dia, horario.desde + ' a ' + horario.hasta))

	horario = horario_restaurante(dias)

	try:
		imagenes = Imagen.objects.filter(restaurante=restaurante)
	except:
		error = 'Este rest no posee imagenes'
	try:
		#Direccion del restaurante y otros datos.
		direccion = Direccion.objects.get(restaurante=restaurante)
		coord = str(direccion.coord).split(',')
		lat = coord[0]
		lng = coord[1]
		direccion = direccion.direccion + '. ' + direccion.zona + ', ' + direccion.ciudad
	except:
		error = 'Este rest no posee direccion'
	try:
		telefonos = TelefonoRestaurante.objects.filter(restaurante=restaurante)
	except:
		error = 'Este rest no posee telefonos'

	#Informacion del plan que utiliza.
	cliente = restaurante.cliente
	plan = restaurante.plan

	#Rango de la cantidad de imagenes.
	rango_img =[]
	for i in range(len(imagenes)):
 		rango_img.append(i)

	#Informacion de los metodos de pago del restaurante.
	metodos = Metodo.objects.all()

	#Servicios que existen
	servicios = Servicio.objects.all()

	#Status en el que se encuentra el restaurante
	disponible = restaurante.abierto

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

	cantidad = len(votos)
	try:
		puntos = puntos/cantidad
	except:
		error = 'Division por cero!'

	ctx = {
		'registro': registro, 
		'buscador': buscador, 
		'restaurante': restaurante,
		'categorias': categorias,  
		'rango_img': rango_img, 
		'logo': logo, 
		'puntos': puntos, 
		'direccion': direccion, 
		'descripcion': descripcion, 
		'horario':horario, 
		'votos': cantidad, 
		'lat': lat, 
		'lng': lng,
		'plan': plan, 
		'servicios_rest': servicios_rest, 
		'servicios': servicios, 
		'metodos_rest': metodos_rest, 
		'metodos': metodos, 
		'telefonos': telefonos,
		'disponible': disponible, 
		'platos': platos, 
		'arreglo': arreglo
	}
	return render_to_response('perfil/perfil.html', ctx, context_instance=RequestContext(request))


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
			restaurantes = Restaurante.objects.filter(direccion__ciudad__icontains=palabra, visibilidad='Público',status='Activo')
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
            return model.objects.filter(q)
    else:
        # Return an empty result
        return {}