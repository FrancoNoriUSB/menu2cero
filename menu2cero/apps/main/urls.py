from django.conf.urls import *

#Urls para los views de los clientes
urlpatterns = patterns('menu2cero.apps.main.views',
	url(r'^$', 'index', name='index'),
	url(r'^restaurante/(?P<id_rest>[0-9]+)/(?P<restaurante>[-_\w]+)*/$', 'restaurante_view', name='restaurante'), #Cambiar url por algo del tipo menu2cero.com/restaurante/categoria/nombre
	url(r'^restaurantes/(?P<palabra>.*)$', 'restaurantes_view', name='restaurantes'),
	url(r'^contactos/$', 'contactos_view', name='contactos'),
	url(r'^votacion/$', 'votacion_view', name='votacion'),
	)