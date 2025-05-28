from app import db 
from datetime import datetime

class OpcionProducto(db.Model):
    __tablename__ = 'opciones_producto'

    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    precio_adicional = db.Column(db.Numeric(10, 2), default=0)
    disponible = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    producto = db.relationship('Producto', back_populates='opciones')

    def __repr__(self):
        return f'<OpcionProducto {self.id} - {self.nombre}>'
