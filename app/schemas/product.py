# app/schemas/product.py
from marshmallow import Schema, fields

class ProductSchema(Schema):
    id = fields.Int(dump_only=True)
    nombre = fields.Str(required=True)
    descripcion = fields.Str()
    precio = fields.Float(required=True)
    imagen_url = fields.Str()
    tiempo_preparacion = fields.Int()
    categoria_id = fields.Int(required=True)
    disponible = fields.Bool(default=True)
    destacado = fields.Bool(default=False)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # Relación con la categoría
    categoria = fields.Nested('CategorySchema', only=['id', 'nombre'])  # Incluye un sub-esquema para Category
    
    # Relación con las opciones del producto
    opciones = fields.List(fields.Nested('ProductOptionSchema', only=['id', 'nombre', 'valor']))
    
    # Relación con las valoraciones
    valoraciones = fields.List(fields.Nested('ReviewSchema', only=['id', 'comentario', 'rating']))
    
    def to_dict(self, obj):
        """Este método permite convertir el objeto Producto en un diccionario
        teniendo en cuenta las relaciones (categoría, opciones, valoraciones).
        """
        product_dict = {
            'id': obj.id,
            'nombre': obj.nombre,
            'descripcion': obj.descripcion,
            'precio': float(obj.precio),
            'imagen_url': obj.imagen_url,
            'tiempo_preparacion': obj.tiempo_preparacion,
            'categoria_id': obj.categoria_id,
            'disponible': obj.disponible,
            'destacado': obj.destacado,
            'created_at': obj.created_at.isoformat() if obj.created_at else None,
            'updated_at': obj.updated_at.isoformat() if obj.updated_at else None,
            'categoria': obj.categoria.to_dict() if obj.categoria else None,  # Relación con Categoria
            'opciones': [op.to_dict() for op in obj.opciones],  # Relación con ProductOption
            'valoraciones': [rev.to_dict() for rev in obj.valoraciones],  # Relación con Review
        }
        return product_dict
