"""
Middleware para manejar excepciones de manera global en la API.
Implementa el principio Open/Closed (OCP) al permitir extender el manejo
de excepciones sin modificar el código existente.
"""
import logging
import traceback
from django.http import JsonResponse
from rest_framework import status

from .exceptions import APIException

logger = logging.getLogger(__name__)


class APIExceptionMiddleware:
    """
    Middleware para capturar y manejar excepciones de la API de manera consistente.
    Proporciona respuestas de error en formato JSON con códigos de estado HTTP apropiados.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_exception(self, request, exception):
        """
        Procesa las excepciones capturadas durante la ejecución de la vista.
        Convierte las excepciones en respuestas JSON con formato consistente.
        """
        # Si es una excepción personalizada de nuestra API
        if isinstance(exception, APIException):
            return JsonResponse(
                {
                    'error': {
                        'code': exception.code,
                        'message': str(exception),
                    }
                },
                status=exception.status_code
            )
        
        # Para otras excepciones, registrar el error y devolver una respuesta genérica
        logger.error(f"Error no manejado: {str(exception)}")
        logger.error(traceback.format_exc())
        
        return JsonResponse(
            {
                'error': {
                    'code': 'server_error',
                    'message': 'Ha ocurrido un error en el servidor.',
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
