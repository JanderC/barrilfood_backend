# app/models/inventory.py
from app.models import db
from datetime import datetime

class Inventario(db.Model):
    __tablename__ = 'inventario'
    __table_args__ = {'schema': 'barrilfood'}
    
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('barrilfood.productos.id', ondelete='CASCADE'))
    cantidad = db.Column(db.Integer, nullable=False, default=0)
    unidad_medida = db.Column(db.String(20))
    alerta_minimo = db.Column(db.Integer)
    ultima_reposicion = db.Column(db.TIMESTAMP)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Inventario {self.producto_id}: {self.cantidad} {self.unidad_medida}>'
    
    def necesita_reposicion(self):
        if self.alerta_minimo is None:
            return False
        return self.cantidad <= self.alerta_minimo
    
    def to_dict(self):
        return {
            'id': self.id,
            'producto_id': self.producto_id,
            'cantidad': self.cantidad,
            'unidad_medida': self.unidad_medida,
            'alerta_minimo': self.alerta_minimo,
            'ultima_reposicion': self.ultima_reposicion.isoformat() if self.ultima_reposicion else None,
            'necesita_reposicion': self.necesita_reposicion()
        }
    
    @property
    def necesita_reposicion(self):
        """Indica si el producto necesita reposición de stock"""
        return self.cantidad <= self.cantidad_minima