from rest_framework import serializers
from .models import Usuario, ProyectoInmobiliario, UnidadPropiedad


class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Usuario
        fields = ['id', 'rut', 'username', 'email', 'first_name', 'last_name', 'role', 'phone', 'password', 'created_at']
        read_only_fields = ['id', 'created_at']
        
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = Usuario.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class UnidadPropiedadSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnidadPropiedad
        fields = ['id', 'proyecto', 'numero_unidad', 'tipo_unidad', 'metraje_cuadrado', 
                 'precio_venta', 'estado', 'cliente', 'created_at']
        read_only_fields = ['id', 'created_at']


class UnidadPropiedadDetailSerializer(serializers.ModelSerializer):
    cliente = UsuarioSerializer(read_only=True)
    
    class Meta:
        model = UnidadPropiedad
        fields = ['id', 'numero_unidad', 'tipo_unidad', 'metraje_cuadrado', 
                 'precio_venta', 'estado', 'cliente', 'created_at']
        read_only_fields = ['id', 'created_at']


class ProyectoInmobiliarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProyectoInmobiliario
        fields = ['id', 'nombre', 'descripcion', 'ubicacion', 'fecha_inicio', 
                 'fecha_finalizacion', 'estado', 'codigo', 'created_at']
        read_only_fields = ['id', 'created_at']


class ProyectoInmobiliarioDetailSerializer(serializers.ModelSerializer):
    unidades = UnidadPropiedadSerializer(many=True, read_only=True)
    
    class Meta:
        model = ProyectoInmobiliario
        fields = ['id', 'nombre', 'descripcion', 'ubicacion', 'fecha_inicio', 
                 'fecha_finalizacion', 'estado', 'codigo', 'created_at', 'unidades']
        read_only_fields = ['id', 'created_at']
