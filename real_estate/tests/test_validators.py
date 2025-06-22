"""
Pruebas unitarias para los validadores de la aplicación real_estate.
Implementa buenas prácticas de testing para verificar el correcto funcionamiento
de las validaciones de datos.
"""
from django.test import TestCase
from django.utils import timezone
import datetime

from ..validators.usuario_validator import UsuarioValidator
from ..validators.proyecto_validator import ProyectoValidator
from ..validators.unidad_validator import UnidadValidator
from ..models import Usuario, ProyectoInmobiliario, UnidadPropiedad


class UsuarioValidatorTestCase(TestCase):
    """Pruebas para el validador de Usuario"""
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.valid_data = {
            'rut': '12345678-9',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'SecurePass1',
            'role': 'Cliente',
            'username': 'testuser'
        }
    
    def test_valid_data(self):
        """Prueba con datos válidos"""
        validator = UsuarioValidator(self.valid_data)
        self.assertTrue(validator.is_valid())
        self.assertEqual(len(validator.get_error_dict()), 0)
    
    def test_invalid_rut(self):
        """Prueba con RUT inválido"""
        # RUT con formato incorrecto - debe ser 12345678-9
        invalid_data = self.valid_data.copy()
        invalid_data['rut'] = '123456789'
        validator = UsuarioValidator(invalid_data)
        self.assertFalse(validator.is_valid())
        self.assertIn('rut', validator.get_error_dict())
    
    def test_invalid_email(self):
        """Prueba con email inválido"""
        invalid_data = self.valid_data.copy()
        invalid_data['email'] = 'invalid-email'
        validator = UsuarioValidator(invalid_data)
        self.assertFalse(validator.is_valid())
        self.assertIn('email', validator.get_error_dict())
    
    def test_invalid_role(self):
        """Prueba con rol inválido"""
        invalid_data = self.valid_data.copy()
        invalid_data['role'] = 'rol_inexistente'
        validator = UsuarioValidator(invalid_data)
        self.assertFalse(validator.is_valid())
        self.assertIn('role', validator.get_error_dict())
    
    def test_missing_required_fields(self):
        """Prueba con campos requeridos faltantes"""
        # Sin RUT
        invalid_data = self.valid_data.copy()
        del invalid_data['rut']
        validator = UsuarioValidator(invalid_data)
        self.assertFalse(validator.is_valid())
        self.assertIn('rut', validator.get_error_dict())
        
        # Sin email
        invalid_data = self.valid_data.copy()
        del invalid_data['email']
        validator = UsuarioValidator(invalid_data)
        self.assertFalse(validator.is_valid())
        self.assertIn('email', validator.get_error_dict())


class ProyectoValidatorTestCase(TestCase):
    """Pruebas para el validador de ProyectoInmobiliario"""
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.valid_data = {
            'nombre': 'Proyecto Test',
            'descripcion': 'Descripción del proyecto de prueba',
            'ubicacion': 'Dirección Test',
            'fecha_inicio': timezone.now().date(),
            'fecha_finalizacion': (timezone.now() + datetime.timedelta(days=365)).date(),
            'estado': 'En Construcción',
            'codigo': 'TEST002'
        }
    
    def test_valid_data(self):
        """Prueba con datos válidos"""
        # Asegurarse de que el estado sea uno de los valores válidos
        valid_data = self.valid_data.copy()
        valid_data['estado'] = 'En Construcción'
        validator = ProyectoValidator(valid_data)
        self.assertTrue(validator.is_valid())
        self.assertEqual(len(validator.get_error_dict()), 0)
    
    def test_invalid_dates(self):
        """Prueba con fechas inválidas"""
        # Fecha de finalización anterior a fecha de inicio
        invalid_data = self.valid_data.copy()
        invalid_data['fecha_finalizacion'] = (timezone.now() - datetime.timedelta(days=10)).date()
        validator = ProyectoValidator(invalid_data)
        self.assertFalse(validator.is_valid())
        self.assertIn('fecha_finalizacion', validator.get_error_dict())
    
    def test_invalid_estado(self):
        """Prueba con estado inválido"""
        invalid_data = self.valid_data.copy()
        invalid_data['estado'] = 'estado_inexistente'
        validator = ProyectoValidator(invalid_data)
        self.assertFalse(validator.is_valid())
        self.assertIn('estado', validator.get_error_dict())
    
    def test_missing_required_fields(self):
        """Prueba con campos requeridos faltantes"""
        # Sin nombre
        invalid_data = self.valid_data.copy()
        del invalid_data['nombre']
        validator = ProyectoValidator(invalid_data)
        self.assertFalse(validator.is_valid())
        self.assertIn('nombre', validator.get_error_dict())
        
        # Sin ubicación
        invalid_data = self.valid_data.copy()
        del invalid_data['ubicacion']
        validator = ProyectoValidator(invalid_data)
        self.assertFalse(validator.is_valid())
        self.assertIn('ubicacion', validator.get_error_dict())


class UnidadValidatorTestCase(TestCase):
    """Pruebas para el validador de UnidadPropiedad"""
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        # Crear proyecto para las pruebas
        self.proyecto = ProyectoInmobiliario.objects.create(
            nombre='Proyecto Test',
            descripcion='Descripción del proyecto de prueba',
            ubicacion='Dirección Test',
            fecha_inicio=timezone.now().date(),
            fecha_finalizacion=(timezone.now() + datetime.timedelta(days=365)).date(),
            estado='En construcción',
            codigo='TEST001'
        )
        
        self.valid_data = {
            'proyecto': self.proyecto.id,
            'proyecto_id': self.proyecto.id,
            'numero_unidad': 'A101',
            'tipo_unidad': 'Departamento',
            'metraje_cuadrado': 80.5,
            'precio_venta': 5000,
            'estado': 'Disponible'
        }
    
    def test_valid_data(self):
        """Prueba con datos válidos"""
        # Asegurarse de que los valores sean válidos según el validador
        valid_data = self.valid_data.copy()
        valid_data['tipo_unidad'] = 'Departamento'
        valid_data['estado'] = 'Disponible'
        validator = UnidadValidator(valid_data)
        self.assertTrue(validator.is_valid())
        self.assertEqual(len(validator.get_error_dict()), 0)
    
    def test_invalid_proyecto(self):
        """Prueba con proyecto inválido"""
        invalid_data = self.valid_data.copy()
        # Eliminar proyecto_id para forzar error
        del invalid_data['proyecto_id']
        validator = UnidadValidator(invalid_data)
        self.assertFalse(validator.is_valid())
        self.assertIn('proyecto_id', validator.get_error_dict())
    
    def test_invalid_tipo_unidad(self):
        """Prueba con tipo de unidad inválido"""
        invalid_data = self.valid_data.copy()
        invalid_data['tipo_unidad'] = 'tipo_inexistente'
        validator = UnidadValidator(invalid_data)
        self.assertFalse(validator.is_valid())
        self.assertIn('tipo_unidad', validator.get_error_dict())
    
    def test_invalid_estado(self):
        """Prueba con estado inválido"""
        invalid_data = self.valid_data.copy()
        invalid_data['estado'] = 'estado_inexistente'
        validator = UnidadValidator(invalid_data)
        self.assertFalse(validator.is_valid())
        self.assertIn('estado', validator.get_error_dict())
    
    def test_invalid_metraje(self):
        """Prueba con metraje inválido"""
        invalid_data = self.valid_data.copy()
        invalid_data['metraje_cuadrado'] = -10
        validator = UnidadValidator(invalid_data)
        self.assertFalse(validator.is_valid())
        self.assertIn('metraje_cuadrado', validator.get_error_dict())
    
    def test_invalid_precio(self):
        """Prueba con precio inválido"""
        invalid_data = self.valid_data.copy()
        invalid_data['precio_venta'] = -5000
        validator = UnidadValidator(invalid_data)
        self.assertFalse(validator.is_valid())
        self.assertIn('precio_venta', validator.get_error_dict())
    
    def test_missing_required_fields(self):
        """Prueba con campos requeridos faltantes"""
        # Sin proyecto_id
        invalid_data = self.valid_data.copy()
        del invalid_data['proyecto_id']
        validator = UnidadValidator(invalid_data)
        self.assertFalse(validator.is_valid())
        self.assertIn('proyecto_id', validator.get_error_dict())
        
        # Sin número de unidad
        invalid_data = self.valid_data.copy()
        del invalid_data['numero_unidad']
        validator = UnidadValidator(invalid_data)
        self.assertFalse(validator.is_valid())
        self.assertIn('numero_unidad', validator.get_error_dict())
