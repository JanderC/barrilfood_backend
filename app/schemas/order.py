from marshmallow import Schema, fields, validate

class OpcionSchema(Schema):
    opcion_id = fields.Integer(required=True)
    precio = fields.Float(required=True, validate=validate.Range(min=0))

class ProductoOrderSchema(Schema):
    producto_id = fields.Integer(required=True)
    cantidad = fields.Integer(required=True, validate=validate.Range(min=1))
    precio_unitario = fields.Float(required=True, validate=validate.Range(min=0))
    subtotal = fields.Float(required=True, validate=validate.Range(min=0))
    notas = fields.String(allow_none=True, missing='')
    opciones = fields.List(fields.Nested(OpcionSchema), allow_none=True, missing=[])

class OrderCreateSchema(Schema):
    usuario_id = fields.UUID(required=False, allow_none=True)
    # Campos requeridos
    direccion_id = fields.Integer(required=True)
    metodo_pago_id = fields.Integer(required=True)
    subtotal = fields.Float(required=True, validate=validate.Range(min=0))
    total = fields.Float(required=True, validate=validate.Range(min=0))
    items = fields.List(fields.Nested(ProductoOrderSchema), required=True, validate=validate.Length(min=1))
    
    # Campos opcionales con valores por defecto
    costo_envio = fields.Float(allow_none=True, missing=0, validate=validate.Range(min=0))
    descuento = fields.Float(allow_none=True, missing=0, validate=validate.Range(min=0))
    impuestos = fields.Float(allow_none=True, missing=0, validate=validate.Range(min=0))
    notas = fields.String(allow_none=True, missing='')
    
    # Estos campos NO deben estar aquí porque se asignan automáticamente
    # usuario_id se obtiene del JWT
    # estado_id se asigna automáticamente como 1

class OrderSchema(Schema):
    id = fields.UUID()
    usuario_id = fields.UUID()
    direccion_id = fields.Integer()
    estado_id = fields.Integer()
    metodo_pago_id = fields.Integer()
    fecha_pedido = fields.DateTime()
    fecha_entrega_estimada = fields.DateTime(allow_none=True)
    fecha_entrega_real = fields.DateTime(allow_none=True)
    subtotal = fields.Float()
    costo_envio = fields.Float()
    descuento = fields.Float()
    impuestos = fields.Float()
    total = fields.Float()
    notas = fields.String(allow_none=True)
    repartidor_id = fields.UUID(allow_none=True)
    codigo_seguimiento = fields.String(allow_none=True)
    created_at = fields.DateTime()
    updated_at = fields.DateTime()

class OrderDetailSchema(Schema):
    id = fields.UUID()
    usuario_id = fields.UUID()
    estado_id = fields.Integer()
    total = fields.Float()
    fecha_pedido = fields.DateTime()
    productos = fields.List(fields.Nested(ProductoOrderSchema))
    estado_nombre = fields.String()
    metodo_pago_nombre = fields.String()