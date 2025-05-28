# app/models/category.py
from app.models import db
from datetime import datetime

class Categoria(db.Model):
    __tablename__ = 'categorias'
    __table_args__ = {'schema': 'barrilfood'}
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    descripcion = db.Column(db.Text)
    imagen_url = db.Column(db.String(255))
    activo = db.Column(db.Boolean, default=True)
    orden = db.Column(db.Integer)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación con productos
    productos = db.relationship('Producto', backref='categoria', lazy='dynamic')
    
    def __repr__(self):
        return f'<Categoria {self.nombre}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'imagen_url': self.imagen_url,
            'activo': self.activo,
            'orden': self.orden,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }