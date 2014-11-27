from django.contrib import admin
from models import *

#Clase para agregar al admin la tabla de rest
class RestauranteAdmin(admin.TabularInline):
	model = Restaurante
	extra = 0

#Codigo para agregar al admin del cliente la tabla del restaurante
# class ClienteAdmin(admin.ModelAdmin):
# 	list_display = ('nombre',)
# 	list_filter = ('nombre',)
# 	search_fields = ['nombre']
# 	inlines = [RestauranteAdmin]

admin.site.register(Categoria)
admin.site.register(Cliente)
admin.site.register(Comensal)
admin.site.register(Direccion)
admin.site.register(Horario)
admin.site.register(Imagen)
admin.site.register(Menu)
admin.site.register(Metodo)
admin.site.register(Plan)
admin.site.register(Plato)
admin.site.register(Pago)
admin.site.register(Red_social)
admin.site.register(Restaurante)
admin.site.register(Servicio)
admin.site.register(TelefonoRestaurante)
admin.site.register(Voto)