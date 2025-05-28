from app import db
from datetime import datetime

class Direccion(db.Model):
    __tablename__ = 'direcciones'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.String(36), db.ForeignKey('usuarios.id'), nullable=False)
    direccion = db.Column(db.Text, nullable=False)
    ciudad = db.Column(db.String(100), nullable=False)
    barrio = db.Column(db.String(100), nullable=True)
    referencia = db.Column(db.Text, nullable=True)
    latitud = db.Column(db.Numeric(10, 8), nullable=True)
    longitud = db.Column(db.Numeric(11, 8), nullable=True)
    es_principal = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    usuario = db.relationship('Usuario', back_populates='direcciones')

    def __repr__(self):
        return f'<Direccion {self.id} - {self.usuario_id}>'
