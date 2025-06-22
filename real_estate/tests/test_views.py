"""
Pruebas unitarias para las vistas (viewsets) de la aplicación real_estate.
Implementa buenas prácticas de testing para verificar el correcto funcionamiento
de los endpoints de la API.
"""
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
import datetime
import json

from ..models import Usuario, ProyectoInmobiliario, UnidadPropiedad


class UsuarioViewSetTestCase(APITestCase):
    """Pruebas para el viewset de Usuario"""
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.client = APIClient()
        
        # Crear usuario administrador
        self.admin = Usuario.objects.create_user(
            username='admin',
            rut='98765432-1',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            password='adminpassword',
            role='Administrador',
            is_staff=True  # Esto es necesario para que IsAdminUser lo reconozca como administrador
        )
        
        # Crear usuario cliente
        self.cliente = Usuario.objects.create_user(
            username='cliente',
            rut='12345678-9',
            email='cliente@example.com',
            first_name='Cliente',
            last_name='Test',
            password='clientepassword',
            role='Cliente'
        )
        
        # URLs para las pruebas
        self.list_url = reverse('usuario-list')
        self.detail_url = reverse('usuario-detail', args=[self.cliente.id])
        self.clientes_url = reverse('usuario-clientes')
        self.administradores_url = reverse('usuario-administradores')
    
    def test_list_usuarios_authenticated(self):
        """Prueba listar usuarios como usuario autenticado"""
        # Autenticar como administrador
        self.client.force_authenticate(user=self.admin)
        
        # Realizar petición GET
        response = self.client.get(self.list_url)
        
        # Verificar respuesta
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Admin + Cliente
    
    def test_list_usuarios_unauthenticated(self):
        """Prueba listar usuarios sin autenticación"""
        # Realizar petición GET sin autenticación
        response = self.client.get(self.list_url)
        
        # Verificar que se requiere autenticación
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_usuario(self):
        """Prueba crear un usuario"""
        data = {
            'username': 'nuevo_usuario',
            'rut': '11111111-1',
            'email': 'nuevo@example.com',
            'first_name': 'Nuevo',
            'last_name': 'Usuario',
            'password': 'Password123',
            'role': 'Cliente'
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Usuario.objects.count(), 3)  # 2 iniciales + 1 nuevo
    
    def test_create_usuario_invalid_data(self):
        """Prueba crear un usuario con datos inválidos"""
        # Datos inválidos (sin RUT)
        invalid_data = {
            'email': 'invalido@example.com',
            'first_name': 'Inválido',
            'last_name': 'Usuario',
            'password': 'invalidopassword',
            'role': 'cliente'
        }
        
        # Realizar petición POST
        response = self.client.post(self.list_url, invalid_data, format='json')
        
        # Verificar respuesta de error
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('rut', response.data)
    
    def test_update_usuario_admin(self):
        """Prueba actualizar un usuario como administrador"""
        # Autenticar como administrador
        self.client.force_authenticate(user=self.admin)
        
        data = {
            'first_name': 'ClienteActualizado',
            'last_name': 'TestActualizado',
            'email': self.cliente.email,
            'rut': self.cliente.rut,
            'role': 'Cliente',
            'username': self.cliente.username
        }
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que los datos se actualizaron
        self.cliente.refresh_from_db()
        self.assertEqual(self.cliente.first_name, 'ClienteActualizado')
        self.assertEqual(self.cliente.last_name, 'TestActualizado')
    
    def test_update_usuario_no_admin(self):
        """Prueba actualizar un usuario sin ser administrador"""
        # Autenticar como cliente
        self.client.force_authenticate(user=self.cliente)
        
        # Datos para actualizar
        update_data = {
            'first_name': 'ClienteActualizado',
            'last_name': 'TestActualizado'
        }
        
        # Realizar petición PATCH
        response = self.client.patch(self.detail_url, update_data, format='json')
        
        # Verificar que se requiere ser administrador
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_delete_usuario_admin(self):
        """Prueba eliminar un usuario como administrador"""
        # Autenticar como administrador
        self.client.force_authenticate(user=self.admin)
        
        # Realizar petición DELETE
        response = self.client.delete(self.detail_url)
        
        # Verificar respuesta
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verificar que el usuario se eliminó de la base de datos
        self.assertFalse(Usuario.objects.filter(id=self.cliente.id).exists())
    
    def test_delete_usuario_no_admin(self):
        """Prueba eliminar un usuario sin ser administrador"""
        # Autenticar como cliente
        self.client.force_authenticate(user=self.cliente)
        
        # Realizar petición DELETE
        response = self.client.delete(self.detail_url)
        
        # Verificar que se requiere ser administrador
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_get_clientes(self):
        """Prueba obtener todos los clientes"""
        # Autenticar como administrador
        self.client.force_authenticate(user=self.admin)
        
        response = self.client.get(self.clientes_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Solo hay un cliente
        self.assertEqual(response.data['results'][0]['role'], 'Cliente')
    
    def test_get_administradores(self):
        """Prueba obtener todos los administradores"""
        # Autenticar como administrador
        self.client.force_authenticate(user=self.admin)
        
        response = self.client.get(self.administradores_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Solo hay un administrador
        self.assertEqual(response.data['results'][0]['role'], 'Administrador')


class ProyectoInmobiliarioViewSetTestCase(APITestCase):
    """Pruebas para el viewset de ProyectoInmobiliario"""
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.client = APIClient()
        
        # Crear usuario administrador
        self.admin = Usuario.objects.create_user(
            username='admin',
            rut='98765432-1',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            password='adminpassword',
            role='Administrador',
            is_staff=True  # Esto es necesario para que IsAdminUser lo reconozca como administrador
        )
        
        # Crear usuario cliente
        self.cliente = Usuario.objects.create_user(
            username='cliente',
            rut='12345678-9',
            email='cliente@example.com',
            first_name='Cliente',
            last_name='Test',
            password='clientepassword',
            role='Cliente'
        )
        
        # Crear proyecto de prueba
        self.proyecto = ProyectoInmobiliario.objects.create(
            nombre='Proyecto Test',
            descripcion='Descripción del proyecto de prueba',
            ubicacion='Dirección Test',
            fecha_inicio=timezone.now().date(),
            fecha_finalizacion=(timezone.now() + datetime.timedelta(days=365)).date(),
            estado='En Construcción',
            codigo='TEST001'
        )
        
        # URLs para las pruebas
        self.list_url = reverse('proyectoinmobiliario-list')
        self.detail_url = reverse('proyectoinmobiliario-detail', args=[self.proyecto.id])
        self.search_url = reverse('proyectoinmobiliario-search')
        self.estadisticas_url = reverse('proyectoinmobiliario-estadisticas')
    
    def test_list_proyectos_authenticated(self):
        """Prueba listar proyectos como usuario autenticado"""
        # Autenticar como cliente
        self.client.force_authenticate(user=self.cliente)
        
        # Realizar petición GET
        response = self.client.get(self.list_url)
        
        # Verificar respuesta
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Solo hay un proyecto
    
    def test_list_proyectos_unauthenticated(self):
        """Prueba listar proyectos sin autenticación"""
        # Realizar petición GET sin autenticación
        response = self.client.get(self.list_url)
        
        # Verificar que se requiere autenticación
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_proyecto_admin(self):
        """Prueba crear un proyecto como administrador"""
        # Autenticar como administrador
        self.client.force_authenticate(user=self.admin)
        
        data = {
            'nombre': 'Nuevo Proyecto',
            'descripcion': 'Descripción del nuevo proyecto',
            'ubicacion': 'Nueva Ubicación',
            'fecha_inicio': timezone.now().date().isoformat(),
            'fecha_finalizacion': (timezone.now() + datetime.timedelta(days=365)).date().isoformat(),
            'estado': 'En Construcción',
            'codigo': 'NUEVO001'
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProyectoInmobiliario.objects.count(), 2)  # 1 inicial + 1 nuevo
    
    def test_create_proyecto_no_admin(self):
        """Prueba crear un proyecto sin ser administrador"""
        # Autenticar como cliente
        self.client.force_authenticate(user=self.cliente)
        
        # Datos para el nuevo proyecto
        new_proyecto_data = {
            'nombre': 'Nuevo Proyecto',
            'descripcion': 'Descripción del nuevo proyecto',
            'ubicacion': 'Nueva Dirección',
            'fecha_inicio': timezone.now().date().isoformat(),
            'fecha_finalizacion': (timezone.now() + datetime.timedelta(days=365)).date().isoformat(),
            'estado': 'En construcción'
        }
        
        # Realizar petición POST
        response = self.client.post(self.list_url, new_proyecto_data, format='json')
        
        # Verificar que se requiere ser administrador
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_proyecto_admin(self):
        """Prueba actualizar un proyecto como administrador"""
        # Autenticar como administrador
        self.client.force_authenticate(user=self.admin)
        
        data = {
            'nombre': 'Proyecto Actualizado',
            'descripcion': 'Descripción actualizada',
            'ubicacion': 'Ubicación de prueba actualizada',
            'fecha_inicio': self.proyecto.fecha_inicio.isoformat(),
            'fecha_finalizacion': self.proyecto.fecha_finalizacion.isoformat(),
            'estado': 'En Construcción',
            'codigo': self.proyecto.codigo
        }
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que los datos se actualizaron
        self.proyecto.refresh_from_db()
        self.assertEqual(self.proyecto.nombre, 'Proyecto Actualizado')
        self.assertEqual(self.proyecto.descripcion, 'Descripción actualizada')
    
    def test_update_proyecto_no_admin(self):
        """Prueba actualizar un proyecto sin ser administrador"""
        # Autenticar como cliente
        self.client.force_authenticate(user=self.cliente)
        
        # Datos para actualizar
        update_data = {
            'nombre': 'Proyecto Actualizado',
            'ubicacion': 'Dirección Actualizada'
        }
        
        # Realizar petición PATCH
        response = self.client.patch(self.detail_url, update_data, format='json')
        
        # Verificar que se requiere ser administrador
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_delete_proyecto_admin(self):
        """Prueba eliminar un proyecto como administrador"""
        # Autenticar como administrador
        self.client.force_authenticate(user=self.admin)
        
        # Realizar petición DELETE
        response = self.client.delete(self.detail_url)
        
        # Verificar respuesta
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verificar que el proyecto se eliminó de la base de datos
        self.assertFalse(ProyectoInmobiliario.objects.filter(id=self.proyecto.id).exists())
    
    def test_delete_proyecto_no_admin(self):
        """Prueba eliminar un proyecto sin ser administrador"""
        # Autenticar como cliente
        self.client.force_authenticate(user=self.cliente)
        
        # Realizar petición DELETE
        response = self.client.delete(self.detail_url)
        
        # Verificar que se requiere ser administrador
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_search_proyectos(self):
        """Prueba buscar proyectos"""
        # Autenticar como cliente
        self.client.force_authenticate(user=self.cliente)
        
        # Realizar petición GET con parámetros de búsqueda
        response = self.client.get(f"{self.search_url}?nombre=Test")
        
        # Verificar respuesta
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Solo hay un proyecto que coincide
        self.assertEqual(response.data['results'][0]['nombre'], self.proyecto.nombre)
    
    def test_estadisticas_proyectos(self):
        """Prueba obtener estadísticas de proyectos"""
        # Autenticar como administrador
        self.client.force_authenticate(user=self.admin)
        
        # Realizar petición GET
        response = self.client.get(self.estadisticas_url)
        
        # Verificar respuesta
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_proyectos', response.data)
        self.assertIn('proyectos_por_estado', response.data)
        self.assertEqual(response.data['total_proyectos'], 1)  # Solo hay un proyecto
        self.assertEqual(response.data['proyectos_por_estado']['En Construcción'], 1)


class UnidadPropiedadViewSetTestCase(APITestCase):
    """Pruebas para el viewset de UnidadPropiedad"""
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.client = APIClient()
        
        # Crear usuario administrador
        self.admin = Usuario.objects.create_user(
            username='admin',
            rut='98765432-1',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            password='adminpassword',
            role='Administrador',
            is_staff=True  # Esto es necesario para que IsAdminUser lo reconozca como administrador
        )
        
        # Crear usuario cliente
        self.cliente = Usuario.objects.create_user(
            username='cliente',
            rut='12345678-9',
            email='cliente@example.com',
            first_name='Cliente',
            last_name='Test',
            password='clientepassword',
            role='Cliente'
        )
        
        # Crear proyecto de prueba
        self.proyecto = ProyectoInmobiliario.objects.create(
            nombre='Proyecto Test',
            descripcion='Descripción del proyecto de prueba',
            ubicacion='Dirección Test',
            fecha_inicio=timezone.now().date(),
            fecha_finalizacion=(timezone.now() + datetime.timedelta(days=365)).date(),
            estado='En Construcción',
            codigo='TEST001'
        )
        
        # Crear unidad de prueba
        self.unidad = UnidadPropiedad.objects.create(
            proyecto=self.proyecto,
            numero_unidad='A101',
            tipo_unidad='Departamento',
            metraje_cuadrado=80.5,
            precio_venta=5000,
            estado='Disponible'
        )
        
        # URLs para las pruebas
        self.list_url = reverse('unidadpropiedad-list')
        self.detail_url = reverse('unidadpropiedad-detail', args=[self.unidad.id])
        self.por_proyecto_url = reverse('unidadpropiedad-por-proyecto')
        self.disponibles_url = reverse('unidadpropiedad-disponibles')
        self.por_tipo_url = reverse('unidadpropiedad-por-tipo')
        self.por_rango_precio_url = reverse('unidadpropiedad-por-rango-precio')
        self.asignar_cliente_url = reverse('unidadpropiedad-asignar-cliente', args=[self.unidad.id])
        self.marcar_como_vendida_url = reverse('unidadpropiedad-marcar-como-vendida', args=[self.unidad.id])
        self.estadisticas_por_proyecto_url = reverse('unidadpropiedad-estadisticas-por-proyecto')
    
    def test_list_unidades_authenticated(self):
        """Prueba listar unidades como usuario autenticado"""
        # Autenticar como cliente
        self.client.force_authenticate(user=self.cliente)
        
        # Realizar petición GET
        response = self.client.get(self.list_url)
        
        # Verificar respuesta
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Solo hay una unidad
    
    def test_list_unidades_unauthenticated(self):
        """Prueba listar unidades sin autenticación"""
        # Realizar petición GET sin autenticación
        response = self.client.get(self.list_url)
        
        # Verificar que se requiere autenticación
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_unidad_admin(self):
        """Prueba crear una unidad como administrador"""
        # Autenticar como administrador
        self.client.force_authenticate(user=self.admin)
        
        data = {
            'proyecto_id': str(self.proyecto.id),  # Usar proyecto_id y convertir UUID a string
            'numero_unidad': 'B201',
            'tipo_unidad': 'Departamento',
            'metraje_cuadrado': 75.5,
            'precio_venta': 6000000,  # Aumentar el precio para que sea más realista
            'estado': 'Disponible'
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UnidadPropiedad.objects.count(), 2)  # 1 inicial + 1 nuevo
    
    def test_create_unidad_no_admin(self):
        """Prueba crear una unidad sin ser administrador"""
        # Autenticar como cliente
        self.client.force_authenticate(user=self.cliente)
        
        # Datos para la nueva unidad
        new_unidad_data = {
            'proyecto': self.proyecto.id,
            'numero_unidad': 'A102',
            'tipo_unidad': 'departamento',
            'metraje_cuadrado': 90.5,
            'precio_venta': 6000,
            'estado': 'disponible'
        }
        
        # Realizar petición POST
        response = self.client.post(self.list_url, new_unidad_data, format='json')
        
        # Verificar que se requiere ser administrador
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_unidad_admin(self):
        """Prueba actualizar una unidad como administrador"""
        # Autenticar como administrador
        self.client.force_authenticate(user=self.admin)
        
        data = {
            'proyecto_id': str(self.proyecto.id),
            'numero_unidad': self.unidad.numero_unidad,
            'tipo_unidad': self.unidad.tipo_unidad,
            'metraje_cuadrado': self.unidad.metraje_cuadrado,
            'precio_venta': 7000000,  # Precio más realista
            'estado': 'Reservado'
        }
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que los datos se actualizaron
        self.unidad.refresh_from_db()
        self.assertEqual(self.unidad.precio_venta, 7000000)
        self.assertEqual(self.unidad.estado, 'Reservado')
    
    def test_update_unidad_no_admin(self):
        """Prueba actualizar una unidad sin ser administrador"""
        # Autenticar como cliente
        self.client.force_authenticate(user=self.cliente)
        
        # Datos para actualizar
        update_data = {
            'precio_venta': 5500,
            'estado': 'Reservado'
        }
        
        # Realizar petición PATCH
        response = self.client.patch(self.detail_url, update_data, format='json')
        
        # Verificar que se requiere ser administrador
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_delete_unidad_admin(self):
        """Prueba eliminar una unidad como administrador"""
        # Autenticar como administrador
        self.client.force_authenticate(user=self.admin)
        
        # Realizar petición DELETE
        response = self.client.delete(self.detail_url)
        
        # Verificar respuesta
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verificar que la unidad se eliminó de la base de datos
        self.assertFalse(UnidadPropiedad.objects.filter(id=self.unidad.id).exists())
    
    def test_delete_unidad_no_admin(self):
        """Prueba eliminar una unidad sin ser administrador"""
        # Autenticar como cliente
        self.client.force_authenticate(user=self.cliente)
        
        # Realizar petición DELETE
        response = self.client.delete(self.detail_url)
        
        # Verificar que se requiere ser administrador
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_por_proyecto(self):
        """Prueba obtener unidades por proyecto"""
        # Autenticar como cliente
        self.client.force_authenticate(user=self.cliente)
        
        # Realizar petición GET con parámetros
        response = self.client.get(f"{self.por_proyecto_url}?proyecto_id={self.proyecto.id}")
        
        # Verificar respuesta
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Solo hay una unidad en este proyecto
        self.assertEqual(response.data['results'][0]['numero_unidad'], self.unidad.numero_unidad)
    
    def test_disponibles(self):
        """Prueba obtener unidades disponibles"""
        # Autenticar como cliente
        self.client.force_authenticate(user=self.cliente)
        
        # Realizar petición GET
        response = self.client.get(self.disponibles_url)
        
        # Verificar respuesta
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Solo hay una unidad disponible
        self.assertEqual(response.data['results'][0]['estado'], 'Disponible')
        
        # Cambiar estado de la unidad
        self.unidad.estado = 'Vendido'
        self.unidad.save()
        
        # Realizar petición GET nuevamente
        response = self.client.get(self.disponibles_url)
        
        # Verificar que ya no hay unidades disponibles
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)
    
    def test_por_tipo(self):
        """Prueba obtener unidades por tipo"""
        # Autenticar como cliente
        self.client.force_authenticate(user=self.cliente)
        
        # Realizar petición GET con parámetros
        response = self.client.get(f"{self.por_tipo_url}?tipo=Departamento")
        
        # Verificar respuesta
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Solo hay una unidad de tipo departamento
        self.assertEqual(response.data['results'][0]['tipo_unidad'], 'Departamento')
    
    def test_por_rango_precio(self):
        """Prueba obtener unidades por rango de precio"""
        # Autenticar como cliente
        self.client.force_authenticate(user=self.cliente)
        
        # Realizar petición GET con parámetros
        response = self.client.get(f"{self.por_rango_precio_url}?desde=4000&hasta=6000")
        
        # Verificar respuesta
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Solo hay una unidad en este rango de precio
        self.assertEqual(float(response.data['results'][0]['precio_venta']), self.unidad.precio_venta)
    
    def test_asignar_cliente(self):
        """Prueba asignar un cliente a una unidad"""
        # Autenticar como administrador
        self.client.force_authenticate(user=self.admin)
        
        data = {
            'cliente_id': str(self.cliente.id)  # Convertir UUID a string
        }
        response = self.client.post(self.asignar_cliente_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['cliente'], str(self.cliente.id))  # Comparar con string
        
        # Verificar que la unidad cambió a estado 'Reservado'
        self.unidad.refresh_from_db()
        self.assertEqual(self.unidad.estado, 'Reservado')
        self.assertEqual(self.unidad.cliente, self.cliente)
    
    def test_marcar_como_vendida(self):
        """Prueba marcar una unidad como vendida"""
        # Autenticar como administrador
        self.client.force_authenticate(user=self.admin)
        
        # Primero asignar un cliente
        self.unidad.cliente = self.cliente
        self.unidad.estado = 'Reservado'
        self.unidad.save()
        
        # Realizar petición POST
        response = self.client.post(self.marcar_como_vendida_url, {}, format='json')
        
        # Verificar respuesta
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['estado'], 'Vendido')
        
        # Verificar que la unidad se actualizó en la base de datos
        self.unidad.refresh_from_db()
        self.assertEqual(self.unidad.estado, 'Vendido')
    
    def test_estadisticas_por_proyecto(self):
        """Prueba obtener estadísticas por proyecto"""
        # Autenticar como administrador
        self.client.force_authenticate(user=self.admin)
        
        # Realizar petición GET con parámetros
        response = self.client.get(f"{self.estadisticas_por_proyecto_url}?proyecto_id={self.proyecto.id}")
        
        # Verificar respuesta
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_unidades', response.data)
        self.assertIn('unidades_por_estado', response.data)
        self.assertIn('unidades_por_tipo', response.data)
        self.assertIn('precio_promedio', response.data)
        self.assertEqual(response.data['total_unidades'], 1)  # Solo hay una unidad en este proyecto
        self.assertEqual(response.data['unidades_por_estado']['Disponible'], 1)
        self.assertEqual(response.data['unidades_por_tipo']['Departamento'], 1)
        self.assertEqual(response.data['precio_promedio'], 5000)
