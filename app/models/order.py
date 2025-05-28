# app/models/order.py
from app.models import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

class EstadoPedido(db.Model):
    __tablename__ = 'estados_pedido'
    __table_args__ = {'schema': 'barrilfood'}
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    color = db.Column(db.String(7))
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    pedidos = db.relationship('Pedido', backref='estado', lazy='dynamic')
    historiales = db.relationship('HistorialEstadoPedido', backref='estado', lazy='dynamic')
    
    def __repr__(self):
        return f'<EstadoPedido {self.nombre}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'color': self.color
        }

class MetodoPago(db.Model):
    __tablename__ = 'metodos_pago'
    __table_args__ = {'schema': 'barrilfood'}
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    pedidos = db.relationship('Pedido', backref='metodo_pago', lazy='dynamic')
    
    def __repr__(self):
        return f'<MetodoPago {self.nombre}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'activo': self.activo
        }

class Pedido(db.Model):
    __tablename__ = 'pedidos'
    __table_args__ = {'schema': 'barrilfood'}
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = db.Column(UUID(as_uuid=True), db.ForeignKey('barrilfood.usuarios.id'))
    direccion_id = db.Column(db.Integer, db.ForeignKey('barrilfood.direcciones.id'))
    estado_id = db.Column(db.Integer, db.ForeignKey('barrilfood.estados_pedido.id'))
    metodo_pago_id = db.Column(db.Integer, db.ForeignKey('barrilfood.metodos_pago.id'))
    fecha_pedido = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    fecha_entrega_estimada = db.Column(db.TIMESTAMP)
    fecha_entrega_real = db.Column(db.TIMESTAMP)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    costo_envio = db.Column(db.Numeric(10, 2), default=0)
    descuento = db.Column(db.Numeric(10, 2), default=0)
    impuestos = db.Column(db.Numeric(10, 2), default=0)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    notas = db.Column(db.Text)
    repartidor_id = db.Column(UUID(as_uuid=True), db.ForeignKey('barrilfood.usuarios.id'))
    codigo_seguimiento = db.Column(db.String(20))
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    detalles = db.relationship('DetallePedido', backref='pedido', lazy='dynamic', cascade='all, delete-orphan')
    historial_estados = db.relationship('HistorialEstadoPedido', backref='pedido', lazy='dynamic', cascade='all, delete-orphan')
    valoraciones = db.relationship('Valoracion', backref='pedido', lazy='dynamic')
    
    def __repr__(self):
        return f'<Pedido {self.id}>'
    
    def estado_actual(self):
        return self.estado.nombre if self.estado else None
    
    def tiempo_preparacion_total(self):
        return sum(detalle.producto.tiempo_preparacion * detalle.cantidad for detalle in self.detalles)
    
    def to_dict(self, include_details=False):
        result = {
            'id': str(self.id),
            'fecha_pedido': self.fecha_pedido.isoformat(),
            'fecha_entrega_estimada': self.fecha_entrega_estimada.isoformat() if self.fecha_entrega_estimada else None,
            'fecha_entrega_real': self.fecha_entrega_real.isoformat() if self.fecha_entrega_real else None,
            'subtotal': float(self.subtotal),
            'costo_envio': float(self.costo_envio),
            'descuento': float(self.descuento),
            'impuestos': float(self.impuestos),
            'total': float(self.total),
            'notas': self.notas,
            'codigo_seguimiento': self.codigo_seguimiento,
            'estado': self.estado.nombre if self.estado else None,
            'metodo_pago': self.metodo_pago.nombre if self.metodo_pago else None,
            'cliente': self.cliente.nombre_completo if self.cliente else None,
            'repartidor': self.repartidor.nombre_completo if self.repartidor else None
        }
        
        if include_details:
            result['detalles'] = [detalle.to_dict() for detalle in self.detalles]
            if self.direccion:
                result['direccion'] = self.direccion.to_dict()
        
        return result

class DetallePedido(db.Model):
    __tablename__ = 'detalles_pedido'
    __table_args__ = {'schema': 'barrilfood'}
    
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(UUID(as_uuid=True), db.ForeignKey('barrilfood.pedidos.id', ondelete='CASCADE'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('barrilfood.productos.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    notas = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    opciones_seleccionadas = db.relationship('OpcionSeleccionada', backref='detalle_pedido', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<DetallePedido {self.id} del pedido {self.pedido_id}>'
    
    def calcular_subtotal(self):
        subtotal_base = float(self.precio_unitario) * self.cantidad
        subtotal_opciones = sum(float(os.precio) for os in self.opciones_seleccionadas)
        return subtotal_base + subtotal_opciones
    
    def to_dict(self):
        return {
            'id': self.id,
            'producto_id': self.producto_id,
            'nombre_producto': self.producto.nombre if self.producto else None,
            'cantidad': self.cantidad,
            'precio_unitario': float(self.precio_unitario),
            'subtotal': float(self.subtotal),
            'notas': self.notas,
            'opciones': [os.to_dict() for os in self.opciones_seleccionadas]
        }

class OpcionSeleccionada(db.Model):
    __tablename__ = 'opciones_seleccionadas'
    __table_args__ = {'schema': 'barrilfood'}
    
    id = db.Column(db.Integer, primary_key=True)
    detalle_pedido_id = db.Column(db.Integer, db.ForeignKey('barrilfood.detalles_pedido.id', ondelete='CASCADE'), nullable=False)
    opcion_id = db.Column(db.Integer, db.ForeignKey('barrilfood.opciones_producto.id'), nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<OpcionSeleccionada {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'opcion_id': self.opcion_id,
            'nombre_opcion': self.opcion.nombre if self.opcion else None,
            'precio': float(self.precio)
        }

class HistorialEstadoPedido(db.Model):
    __tablename__ = 'historial_estados_pedido'
    __table_args__ = {'schema': 'barrilfood'}
    
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(UUID(as_uuid=True), db.ForeignKey('barrilfood.pedidos.id', ondelete='CASCADE'), nullable=False)
    estado_id = db.Column(db.Integer, db.ForeignKey('barrilfood.estados_pedido.id'), nullable=False)
    usuario_id = db.Column(UUID(as_uuid=True), db.ForeignKey('barrilfood.usuarios.id'))
    fecha = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    notas = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<HistorialEstadoPedido {self.pedido_id} -> {self.estado_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'pedido_id': str(self.pedido_id),
            'estado': self.estado.nombre if self.estado else None,
            'usuario': self.usuario.nombre_completo if self.usuario else None,
            'fecha': self.fecha.isoformat(),
            'notas': self.notas
        }