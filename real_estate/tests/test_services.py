"""
Pruebas unitarias para los servicios de la aplicación real_estate.
Implementa buenas prácticas de testing para verificar el correcto funcionamiento
de la lógica de negocio encapsulada en los servicios.
"""
from django.test import TestCase
from django.utils import timezone
import datetime

from ..models import Usuario, ProyectoInmobiliario, UnidadPropiedad
from ..services.usuario_service import UsuarioService
from ..services.proyecto_service import ProyectoService
from ..services.unidad_service import UnidadService
from ..exceptions import UnidadNoDisponibleError, ClienteNoValidoError


class UsuarioServiceTestCase(TestCase):
    """Pruebas para el servicio de Usuario"""
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.service = UsuarioService()
        
        # Crear usuario de prueba
        self.usuario_data = {
            'rut': '12345678-9',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'securepassword',
            'role': 'Cliente'
        }
        
        self.usuario = self.service.create(**self.usuario_data)
    
    def test_create_usuario(self):
        """Prueba la creación de un usuario"""
        # Verificar que el usuario se creó correctamente
        self.assertEqual(self.usuario.rut, self.usuario_data['rut'])
        self.assertEqual(self.usuario.email, self.usuario_data['email'])
        self.assertEqual(self.usuario.first_name, self.usuario_data['first_name'])
        self.assertEqual(self.usuario.last_name, self.usuario_data['last_name'])
        self.assertEqual(self.usuario.role, self.usuario_data['role'])
        
        # Verificar que la contraseña se ha hasheado
        self.assertTrue(self.usuario.check_password(self.usuario_data['password']))
    
    def test_get_by_role(self):
        """Prueba la obtención de usuarios por rol"""
        # Crear un usuario administrador
        admin_data = {
            'rut': '98765432-1',
            'email': 'admin@example.com',
            'username': 'admin@example.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'password': 'adminpassword',
            'role': 'Administrador'
        }
        self.service.create(**admin_data)
        
        # Obtener usuarios por rol
        clientes = self.service.get_clientes()
        administradores = self.service.get_administradores()
        
        # Verificar resultados
        self.assertEqual(clientes.count(), 1)
        self.assertEqual(administradores.count(), 1)
        self.assertEqual(clientes.first().role, 'Cliente')
        self.assertEqual(administradores.first().role, 'Administrador')
    
    def test_update_usuario(self):
        """Prueba la actualización de un usuario"""
        # Datos para actualizar
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        
        # Actualizar usuario
        updated_usuario = self.service.update(self.usuario.id, **update_data)
        
        # Verificar actualización
        self.assertEqual(updated_usuario.first_name, update_data['first_name'])
        self.assertEqual(updated_usuario.last_name, update_data['last_name'])
        
        # Verificar que otros campos no cambiaron
        self.assertEqual(updated_usuario.rut, self.usuario_data['rut'])
        self.assertEqual(updated_usuario.email, self.usuario_data['email'])
    
    def test_delete_usuario(self):
        """Prueba la eliminación de un usuario"""
        # Eliminar usuario
        self.service.delete(self.usuario.id)
        
        # Verificar que el usuario ya no existe
        with self.assertRaises(Usuario.DoesNotExist):
            Usuario.objects.get(id=self.usuario.id)


class ProyectoServiceTestCase(TestCase):
    """Pruebas para el servicio de ProyectoInmobiliario"""
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.service = ProyectoService()
        
        # Crear proyecto de prueba
        self.proyecto_data = {
            'nombre': 'Proyecto Test',
            'ubicacion': 'Dirección Test',
            'fecha_inicio': timezone.now().date(),
            'fecha_finalizacion': (timezone.now() + datetime.timedelta(days=365)).date(),
            'estado': 'En Construcción',
            'codigo': 'TEST001'
        }
        
        self.proyecto = self.service.create(**self.proyecto_data)
    
    def test_create_proyecto(self):
        """Prueba la creación de un proyecto inmobiliario"""
        # Verificar que el proyecto se creó correctamente
        self.assertEqual(self.proyecto.nombre, self.proyecto_data['nombre'])
        self.assertEqual(self.proyecto.ubicacion, self.proyecto_data['ubicacion'])
        self.assertEqual(self.proyecto.fecha_inicio, self.proyecto_data['fecha_inicio'])
        self.assertEqual(self.proyecto.fecha_finalizacion, self.proyecto_data['fecha_finalizacion'])
        self.assertEqual(self.proyecto.estado, self.proyecto_data['estado'])
        
        # Verificar que se generó un código único
        self.assertIsNotNone(self.proyecto.codigo)
        self.assertTrue(len(self.proyecto.codigo) > 0)
    
    def test_search_advanced(self):
        """Prueba la búsqueda avanzada de proyectos"""
        # Buscar por nombre
        resultados = self.service.search_advanced(nombre='Test')
        self.assertEqual(resultados.count(), 1)
        self.assertEqual(resultados.first().id, self.proyecto.id)
        
        # Buscar por ubicación
        resultados = self.service.search_advanced(ubicacion='Dirección')
        self.assertEqual(resultados.count(), 1)
        self.assertEqual(resultados.first().id, self.proyecto.id)
        
        # Buscar por código
        resultados = self.service.search_advanced(codigo=self.proyecto.codigo)
        self.assertEqual(resultados.count(), 1)
        self.assertEqual(resultados.first().id, self.proyecto.id)
    
    def test_get_estadisticas(self):
        """Prueba la obtención de estadísticas de proyectos"""
        # Obtener estadísticas
        stats = self.service.get_estadisticas()
        
        # Verificar estructura de estadísticas
        self.assertIn('total_proyectos', stats)
        self.assertIn('proyectos_por_estado', stats)
        
        # Verificar valores
        self.assertEqual(stats['total_proyectos'], 1)
        self.assertEqual(stats['proyectos_por_estado']['En Construcción'], 1)


class UnidadServiceTestCase(TestCase):
    """Pruebas para el servicio de UnidadPropiedad"""
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        # Crear servicios
        self.proyecto_service = ProyectoService()
        self.usuario_service = UsuarioService()
        self.unidad_service = UnidadService()
        
        # Crear proyecto de prueba
        self.proyecto_data = {
            'nombre': 'Proyecto Test',
            'ubicacion': 'Dirección Test',
            'fecha_inicio': timezone.now().date(),
            'fecha_finalizacion': (timezone.now() + datetime.timedelta(days=365)).date(),
            'estado': 'En Construcción',
            'codigo': 'TEST001'
        }
        self.proyecto = self.proyecto_service.create(**self.proyecto_data)
        
        # Crear usuario cliente
        self.cliente_data = {
            'rut': '12345678-9',
            'email': 'cliente@example.com',
            'first_name': 'Cliente',
            'last_name': 'Test',
            'password': 'clientepassword',
            'role': 'Cliente'
        }
        self.cliente = self.usuario_service.create(**self.cliente_data)
        
        # Crear unidad de prueba
        self.unidad_data = {
            'proyecto_id': str(self.proyecto.id),
            'numero_unidad': 'A101',
            'tipo_unidad': 'Departamento',
            'metraje_cuadrado': 80.5,
            'precio_venta': 5000000,
            'estado': 'Disponible'
        }
        self.unidad = self.unidad_service.create(**self.unidad_data)
    
    def test_create_unidad(self):
        """Prueba la creación de una unidad de propiedad"""
        # Verificar que la unidad se creó correctamente
        self.assertEqual(self.unidad.proyecto, self.proyecto)
        self.assertEqual(self.unidad.numero_unidad, self.unidad_data['numero_unidad'])
        self.assertEqual(self.unidad.tipo_unidad, self.unidad_data['tipo_unidad'])
        self.assertEqual(self.unidad.metraje_cuadrado, self.unidad_data['metraje_cuadrado'])
        self.assertEqual(self.unidad.precio_venta, self.unidad_data['precio_venta'])
        self.assertEqual(self.unidad.estado, self.unidad_data['estado'])
    
    def test_get_by_proyecto(self):
        """Prueba la obtención de unidades por proyecto"""
        # Obtener unidades por proyecto
        unidades = self.unidad_service.get_by_proyecto(self.proyecto.id)
        
        # Verificar resultados
        self.assertEqual(unidades.count(), 1)
        self.assertEqual(unidades.first().id, self.unidad.id)
    
    def test_get_disponibles(self):
        """Prueba la obtención de unidades disponibles"""
        # Obtener unidades disponibles
        unidades = self.unidad_service.get_disponibles()
        
        # Verificar resultados
        self.assertEqual(unidades.count(), 1)
        self.assertEqual(unidades.first().id, self.unidad.id)
        
        # Marcar unidad como reservada
        self.unidad.estado = 'Reservado'
        self.unidad.save()
        
        # Verificar que ya no aparece como disponible
        unidades = self.unidad_service.get_disponibles()
        self.assertEqual(unidades.count(), 0)
    
    def test_asignar_cliente(self):
        """Prueba la asignación de un cliente a una unidad"""
        # Asignar cliente a unidad
        unidad_actualizada = self.unidad_service.asignar_cliente(self.unidad.id, self.cliente.id)
        
        # Verificar asignación
        self.assertEqual(unidad_actualizada.cliente, self.cliente)
        self.assertEqual(unidad_actualizada.estado, 'Reservado')
    
    def test_asignar_cliente_no_disponible(self):
        """Prueba la asignación de un cliente a una unidad no disponible"""
        # Marcar unidad como vendida
        self.unidad.estado = 'Vendido'
        self.unidad.save()
        
        # Intentar asignar cliente a unidad vendida
        with self.assertRaises(UnidadNoDisponibleError):
            self.unidad_service.asignar_cliente(self.unidad.id, self.cliente.id)
    
    def test_marcar_como_vendida(self):
        """Prueba marcar una unidad como vendida"""
        # Asignar cliente primero
        self.unidad_service.asignar_cliente(self.unidad.id, self.cliente.id)
        
        # Marcar como vendida
        unidad_actualizada = self.unidad_service.marcar_como_vendida(self.unidad.id)
        
        # Verificar estado
        self.assertEqual(unidad_actualizada.estado, 'Vendido')
    
    def test_marcar_como_vendida_sin_cliente(self):
        """Prueba marcar una unidad como vendida sin cliente asignado"""
        # Cambiar estado a Reservado pero sin cliente
        self.unidad.estado = 'Reservado'
        self.unidad.cliente_id = None
        self.unidad.save()
        
        # Intentar marcar como vendida sin cliente
        with self.assertRaises(ClienteNoValidoError):
            self.unidad_service.marcar_como_vendida(self.unidad.id)
    
    def test_get_estadisticas_por_proyecto(self):
        """Prueba la obtención de estadísticas por proyecto"""
        # Obtener estadísticas
        stats = self.unidad_service.get_estadisticas_por_proyecto(self.proyecto.id)
        
        # Verificar estructura de estadísticas
        self.assertIn('total_unidades', stats)
        self.assertIn('unidades_por_estado', stats)
        self.assertIn('unidades_por_tipo', stats)
        self.assertIn('precio_promedio', stats)
        
        # Verificar valores
        self.assertEqual(stats['total_unidades'], 1)
        self.assertEqual(stats['unidades_por_estado']['Disponible'], 1)
        self.assertEqual(stats['unidades_por_tipo']['Departamento'], 1)
        self.assertEqual(stats['precio_promedio'], 5000000)
