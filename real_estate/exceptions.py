"""
Módulo de excepciones personalizadas para la aplicación real_estate.
Implementa el principio de responsabilidad única (SRP) al centralizar
la gestión de excepciones y proporcionar mensajes de error consistentes.
"""
from rest_framework import status


class APIException(Exception):
    """Excepción base para todas las excepciones de la API"""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Ha ocurrido un error en el servidor.'
    default_code = 'error'

    def __init__(self, detail=None, code=None):
        self.detail = detail or self.default_detail
        self.code = code or self.default_code

    def __str__(self):
        return self.detail


class ValidationError(APIException):
    """Excepción para errores de validación"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Los datos proporcionados no son válidos.'
    default_code = 'invalid'


class NotFoundError(APIException):
    """Excepción para recursos no encontrados"""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'El recurso solicitado no existe.'
    default_code = 'not_found'


class PermissionDeniedError(APIException):
    """Excepción para permisos denegados"""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'No tiene permiso para realizar esta acción.'
    default_code = 'permission_denied'


class ConflictError(APIException):
    """Excepción para conflictos de datos"""
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'La operación no puede completarse debido a un conflicto.'
    default_code = 'conflict'


class BusinessLogicError(APIException):
    """Excepción para errores de lógica de negocio"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'La operación no puede completarse debido a reglas de negocio.'
    default_code = 'business_logic_error'


class UnidadNoDisponibleError(BusinessLogicError):
    """Excepción específica para unidades no disponibles"""
    default_detail = 'La unidad no está disponible para esta operación.'
    default_code = 'unidad_no_disponible'


class ClienteNoValidoError(BusinessLogicError):
    """Excepción específica para clientes no válidos"""
    default_detail = 'El cliente no es válido para esta operación.'
    default_code = 'cliente_no_valido'


class ProyectoNoValidoError(BusinessLogicError):
    """Excepción específica para proyectos no válidos"""
    default_detail = 'El proyecto no es válido para esta operación.'
    default_code = 'proyecto_no_valido'
