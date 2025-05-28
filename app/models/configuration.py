# app/models/configuration.py
from app.models import db
from datetime import datetime

class Configuracion(db.Model):
    __tablename__ = 'configuracion'
    __table_args__ = {'schema': 'barrilfood'}
    
    id = db.Column(db.Integer, primary_key=True)
    clave = db.Column(db.String(50), unique=True, nullable=False)
    valor = db.Column(db.Text)
    descripcion = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Configuracion {self.clave}>'
    
    @classmethod
    def get_valor(cls, clave, default=None):
        config = cls.query.filter_by(clave=clave).first()
        if config:
            return config.valor
        return default
    
    @classmethod
    def set_valor(cls, clave, valor, descripcion=None):
        config = cls.query.filter_by(clave=clave).first()
        if config:
            config.valor = valor
            if descripcion:
                config.descripcion = descripcion
        else:
            config = cls(clave=clave, valor=valor, descripcion=descripcion)
            db.session.add(config)
        db.session.commit()
        return config
    
    def to_dict(self):
        return {
            'id': self.id,
            'clave': self.clave,
            'valor': self.valor,
            'descripcion': self.descripcion
        }