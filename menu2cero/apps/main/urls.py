from django.conf.urls import *

#Urls para los views de los clientes
urlpatterns = patterns('menu2cero.apps.main.views',
	url(r'^$', 'index', name='index'),
	url(r'^perfil/restaurante=(?P<id_rest>.*)/$', 'perfil_view', name='perfil'),
	url(r'^restaurantes/(?P<palabra>.*)$', 'restaurantes_view', name='restaurantes'),
	)
