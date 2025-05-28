from app import db

class HistorialEstadosPedido(db.Model):
    __tablename__ = 'historial_estados_pedido'

    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    estado_id = db.Column(db.Integer, db.ForeignKey('order_status.id'))
    usuario_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    fecha = db.Column(db.DateTime, default=db.func.now())
    notas = db.Column(db.String(255))

    # Relaciones
    #pedido = db.relationship('Order', backref='historial_estados')
    #estado = db.relationship('EstadosPedido', backref='historial')
    #usuario = db.relationship('Usuario', backref='historial')
