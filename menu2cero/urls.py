from django.conf.urls import patterns, include, url
from django.contrib import admin
from ajax_select import urls as ajax_select_urls
from django.conf import settings
from django.conf.urls.static import static
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'menu2cero.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),    
    (r'^admin/lookups/', include(ajax_select_urls)),

    #Urls del administrador
    url(r'^', include('menu2cero.apps.administrador.urls')),

    #Urls de contenido principal
    url(r'^', include('menu2cero.apps.main.urls')),

    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT,}),

    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT,}),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)