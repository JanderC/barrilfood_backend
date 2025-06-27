# app/schemas/product.py
from marshmallow import Schema, fields, validate, validates, ValidationError

class ProductSchema(Schema):
    id = fields.Int(dump_only=True)
    nombre = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    descripcion = fields.Str(allow_none=True)
    precio = fields.Decimal(required=True, validate=validate.Range(min=0))
    imagen_url = fields.Str(allow_none=True)  # Este campo almacenará el base64
    tiempo_preparacion = fields.Int(allow_none=True, validate=validate.Range(min=0))
    categoria_id = fields.Int(required=True)
    disponible = fields.Bool(missing=True)
    destacado = fields.Bool(missing=False)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # Campos calculados
    calificacion = fields.Method("get_calificacion", dump_only=True)
    opciones = fields.Method("get_opciones", dump_only=True)
    
    def get_calificacion(self, obj):
        """Obtener calificación promedio del producto"""
        return obj.calificacion_promedio()
    
    def get_opciones(self, obj):
        """Obtener opciones del producto"""
        return [opcion.to_dict() for opcion in obj.opciones]
    
    @validates('imagen_url')
    def validate_imagen_url(self, value):
        """Validar que la imagen_url sea un base64 válido si se proporciona"""
        if value and not value.startswith('data:image/'):
            # Si no es base64, podría ser una URL normal, lo permitimos
            pass
        return value

class ProductOptionSchema(Schema):
    id = fields.Int(dump_only=True)
    producto_id = fields.Int(required=True)
    nombre = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    precio_adicional = fields.Decimal(missing=0, validate=validate.Range(min=0))
    disponible = fields.Bool(missing=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

# Schema específico para subir imágenes
class ProductImageSchema(Schema):
    imagen_base64 = fields.Str(required=True)
    
    @validates('imagen_base64')
    def validate_imagen_base64(self, value):
        """Validar formato de imagen base64"""
        if not value.startswith('data:image/'):
            raise ValidationError('El formato debe ser data:image/[tipo];base64,[datos]')
        
        # Validar que tenga el formato correcto
        try:
            header, data = value.split(',', 1)
            if ';base64' not in header:
                raise ValidationError('El formato debe incluir ;base64')
        except ValueError:
            raise ValidationError('Formato de base64 inválido')