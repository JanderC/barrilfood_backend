from app import db
from datetime import datetime
import uuid

class Pedido(db.Model):
    __tablename__ = 'pedidos'

    id = db.Column(db.String(36), primary_key=True, default=uuid.uuid4)
    usuario_id = db.Column(db.String(36), db.ForeignKey('usuarios.id'), nullable=False)
    direccion_id = db.Column(db.Integer, db.ForeignKey('direcciones.id'), nullable=False)
    estado_id = db.Column(db.Integer, db.ForeignKey('estados_pedido.id'), nullable=False)
    metodo_pago_id = db.Column(db.Integer, db.ForeignKey('metodos_pago.id'), nullable=False)
    fecha_pedido = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_entrega_estimada = db.Column(db.DateTime, nullable=True)
    fecha_entrega_real = db.Column(db.DateTime, nullable=True)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    costo_envio = db.Column(db.Numeric(10, 2), default=0)
    descuento = db.Column(db.Numeric(10, 2), default=0)
    impuestos = db.Column(db.Numeric(10, 2), default=0)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    notas = db.Column(db.Text, nullable=True)
    repartidor_id = db.Column(db.String(36), db.ForeignKey('usuarios.id'), nullable=True)
    codigo_seguimiento = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    usuario = db.relationship('Usuario', back_populates='pedidos')
    direccion = db.relationship('Direccion', back_populates='pedidos')
    estado = db.relationship('EstadoPedido', back_populates='pedidos')
    metodo_pago = db.relationship('MetodoPago', back_populates='pedidos')
    detalles = db.relationship('DetallePedido', back_populates='pedido')
    historial_estados = db.relationship('HistorialEstadoPedido', back_populates='pedido')

    def __repr__(self):
        return f'<Pedido {self.id} - {self.usuario_id}>'
