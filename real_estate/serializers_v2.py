from rest_framework import serializers
from .models import Usuario

class UsuarioSerializerV2(serializers.ModelSerializer):
    """
    Serializer V2 para el modelo Usuario con campos adicionales
    y validaciones mejoradas.
    """
    full_name = serializers.SerializerMethodField()
    projects_count = serializers.SerializerMethodField()
    last_login_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'rut', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'is_active', 'created_at', 'last_login', 'last_login_formatted',
            'projects_count'
        ]
        read_only_fields = ['id', 'created_at', 'last_login', 'full_name', 
                           'projects_count', 'last_login_formatted']
    
    def get_full_name(self, obj):
        """Retorna el nombre completo del usuario."""
        return f"{obj.first_name} {obj.last_name}".strip()
    
    def get_projects_count(self, obj):
        """Retorna el número de proyectos asociados al usuario."""
        if obj.role == 'cliente':
            return obj.unidades_asignadas.count()
        return 0
    
    def get_last_login_formatted(self, obj):
        """Retorna la fecha de último login en formato legible."""
        if obj.last_login:
            return obj.last_login.strftime("%d/%m/%Y %H:%M")
        return None
    
    def validate_rut(self, value):
        """Validación mejorada para el RUT chileno."""
        if value and not self._validate_chilean_rut(value):
            raise serializers.ValidationError("RUT inválido. Formato esperado: 12345678-9")
        return value
    
    def _validate_chilean_rut(self, rut):
        """
        Validación básica de formato de RUT chileno.
        Para una validación completa se debería implementar el algoritmo de verificación.
        """
        import re
        return bool(re.match(r'^\d{7,8}-[\dkK]$', rut))


class UsuarioCreateSerializerV2(UsuarioSerializerV2):
    """
    Serializer específico para la creación de usuarios en V2.
    Incluye campos adicionales como password y confirmación.
    """
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta(UsuarioSerializerV2.Meta):
        fields = UsuarioSerializerV2.Meta.fields + ['password', 'password_confirm']
    
    def validate(self, data):
        """Validación para asegurar que las contraseñas coinciden."""
        if data.get('password') != data.get('password_confirm'):
            raise serializers.ValidationError({"password_confirm": "Las contraseñas no coinciden."})
        return data
    
    def create(self, validated_data):
        """Crea un nuevo usuario con la contraseña encriptada."""
        # Eliminar password_confirm del diccionario
        validated_data.pop('password_confirm', None)
        
        # Crear el usuario
        password = validated_data.pop('password', None)
        user = Usuario.objects.create(**validated_data)
        
        if password:
            user.set_password(password)
            user.save()
            
        return user
