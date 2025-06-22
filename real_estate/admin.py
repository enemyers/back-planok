from django.contrib import admin
from .models import Usuario, ProyectoInmobiliario, UnidadPropiedad


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('rut', 'email', 'first_name', 'last_name', 'role', 'phone')
    list_filter = ('role', 'is_active')
    search_fields = ('rut', 'email', 'first_name', 'last_name')
    ordering = ('last_name', 'first_name')


@admin.register(ProyectoInmobiliario)
class ProyectoInmobiliarioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'ubicacion', 'estado', 'fecha_inicio', 'fecha_finalizacion', 'codigo')
    list_filter = ('estado',)
    search_fields = ('nombre', 'ubicacion', 'codigo')
    ordering = ('-created_at',)


@admin.register(UnidadPropiedad)
class UnidadPropiedadAdmin(admin.ModelAdmin):
    list_display = ('numero_unidad', 'proyecto', 'tipo_unidad', 'metraje_cuadrado', 'precio_venta', 'estado')
    list_filter = ('tipo_unidad', 'estado', 'proyecto')
    search_fields = ('numero_unidad', 'proyecto__nombre')
    ordering = ('proyecto', 'numero_unidad')
