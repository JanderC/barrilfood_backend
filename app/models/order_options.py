from app import db


class OpcionesSeleccionadas(db.Model):
    __tablename__ = 'opciones_seleccionadas'
    
    id = db.Column(db.Integer, primary_key=True)
    detalle_pedido_id = db.Column(db.Integer, db.ForeignKey('detalles_pedido.id'), nullable=False)
    opcion_id = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Float, nullable=False)
    
    # Relación con el detalle de pedido
    detalle_pedido = db.relationship('DetallesPedido', back_populates='opciones_seleccionadas')

    def __init__(self, detalle_pedido_id, opcion_id, precio):
        self.detalle_pedido_id = detalle_pedido_id
        self.opcion_id = opcion_id
        self.precio = precio
