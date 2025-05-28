from marshmallow import Schema, fields

class OrderSchema(Schema):
    id = fields.UUID()
    usuario_id = fields.UUID()
    estado_id = fields.Integer()
    total = fields.Float()
    fecha_creacion = fields.DateTime()

class OrderCreateSchema(Schema):
    usuario_id = fields.UUID(required=True)
    estado_id = fields.Integer(required=True)
    productos = fields.List(fields.Dict(), required=True)  # Ajusta según tus necesidades

class OrderDetailSchema(Schema):
    id = fields.UUID()
    usuario_id = fields.UUID()
    estado_id = fields.Integer()
    total = fields.Float()
    productos = fields.List(fields.Dict())  # Detalles de los productos
