from django.conf.urls import *

#Urls para los views de los clientes
urlpatterns = patterns('menu2cero.apps.main.views',
	url(r'^$', 'index', name='index'),
	url(r'^perfil/(?P<id_rest>[0-9]+)/(?P<restaurante>[-_\w]+)*/$', 'perfil_view', name='perfil'),
	url(r'^restaurantes/(?P<palabra>.*)$', 'restaurantes_view', name='restaurantes'),
	url(r'^contactos/$', 'contactos_view', name='contactos'),
	)
