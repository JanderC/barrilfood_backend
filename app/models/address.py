# app/models/address.py
from app.models import db
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

class Direccion(db.Model):
    __tablename__ = 'direcciones'
    __table_args__ = {'schema': 'barrilfood'}
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(UUID(as_uuid=True), db.ForeignKey('barrilfood.usuarios.id', ondelete='CASCADE'), nullable=False)
    direccion = db.Column(db.Text, nullable=False)
    ciudad = db.Column(db.String(100), nullable=False)
    barrio = db.Column(db.String(100))
    referencia = db.Column(db.Text)
    latitud = db.Column(db.Numeric(10, 8))
    longitud = db.Column(db.Numeric(11, 8))
    es_principal = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación con pedidos
    pedidos = db.relationship('Pedido', backref='direccion', lazy='dynamic')
    
    def __repr__(self):
        return f'<Direccion {self.direccion}, {self.ciudad}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'direccion': self.direccion,
            'ciudad': self.ciudad,
            'barrio': self.barrio,
            'referencia': self.referencia,
            'latitud': float(self.latitud) if self.latitud else None,
            'longitud': float(self.longitud) if self.longitud else None,
            'es_principal': self.es_principal
        }