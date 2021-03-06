from django.conf.urls import *

urlpatterns = patterns('menu2cero.apps.administrador.views',

#Urls para los views del administrador
url(r'^login/$', 'loginUser', name='admin_login'),
url(r'^administrador/editar/(?P<id_rest>.*)/(?P<formulario>.*)$', 'admin_editar_restaurante_view', name='admin_editar'),
url(r'^administrador/agregar/$', 'admin_agregar_restaurante_view', name='admin_editar'),
url(r'^administrador/perfil/$', 'admin_perfil_view', name='admin_perfil'),
url(r'^administrador/modificar_contra/$', 'perfil_modificar_password_view', name='modificar_contra'),
url(r'^administrador/abrir_cerrar/(?P<id_rest>.*)$', 'abrir_cerrar_restaurante', name='abrir_cerrar_restaurante'),
url(r'^administrador/visibilidad_restaurante/(?P<id_rest>.*)$', 'visibilidad_restaurante', name='visibilidad_restaurante'),
url(r'^administrador/eliminar/(?P<id_rest>.*)$', 'eliminar_restaurante', name='eliminar_restaurante'),
url(r'^administrador/cerrar_sesion/$', 'cerrar_sesion', name='cerrar_sesion'),
url(r'^administrador/plan/(?P<id_rest>.*)$', 'admin_plan_view', name='admin_plan'),

)