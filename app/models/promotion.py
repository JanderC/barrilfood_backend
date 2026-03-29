# app/models/promotion.py
from app.models import db
from datetime import datetime

class Promocion(db.Model):
    __tablename__ = 'promociones'
    __table_args__ = {'schema': 'barrilfood'}
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True)
    descripcion = db.Column(db.Text)
    tipo = db.Column(db.String(20), nullable=False)  # porcentaje, monto fijo, envío gratis, etc.
    valor = db.Column(db.Numeric(10, 2))
    fecha_inicio = db.Column(db.TIMESTAMP)
    fecha_fin = db.Column(db.TIMESTAMP)
    uso_maximo = db.Column(db.Integer)
    uso_actual = db.Column(db.Integer, default=0)
    minimo_compra = db.Column(db.Numeric(10, 2), default=0)
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Promocion {self.codigo}>'
    
    def es_valida(self):
        now = datetime.utcnow()
        if not self.activo:
            return False
        if self.fecha_inicio and self.fecha_inicio > now:
            return False
        if self.fecha_fin and self.fecha_fin < now:
            return False
        if self.uso_maximo and self.uso_actual >= self.uso_maximo:
            return False
        return True
    
    def to_dict(self):
        return {
            'id': self.id,
            'codigo': self.codigo,
            'descripcion': self.descripcion,
            'tipo': self.tipo,
            'valor': float(self.valor) if self.valor else None,
            'fecha_inicio': self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            'fecha_fin': self.fecha_fin.isoformat() if self.fecha_fin else None,
            'uso_maximo': self.uso_maximo,
            'uso_actual': self.uso_actual,
            'minimo_compra': float(self.minimo_compra) if self.minimo_compra else 0,
            'activo': self.activo,
            'es_valida': self.es_valida()
        }