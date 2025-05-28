from app.models import db
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

class Valoracion(db.Model):
    __tablename__ = 'valoraciones'
    __table_args__ = (
        db.CheckConstraint('calificacion BETWEEN 1 AND 5'),
        {'schema': 'barrilfood'}  # El diccionario de opciones siempre debe ir al final
    )
    
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(UUID(as_uuid=True), db.ForeignKey('barrilfood.pedidos.id'))
    usuario_id = db.Column(UUID(as_uuid=True), db.ForeignKey('barrilfood.usuarios.id'))
    producto_id = db.Column(db.Integer, db.ForeignKey('barrilfood.productos.id'))
    calificacion = db.Column(db.Integer, nullable=False)
    comentario = db.Column(db.Text)
    fecha = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Valoracion {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'pedido_id': str(self.pedido_id) if self.pedido_id else None,
            'usuario': self.usuario.nombre_completo if self.usuario else None,
            'producto': self.producto.nombre if self.producto else None,
            'calificacion': self.calificacion,
            'comentario': self.comentario,
            'fecha': self.fecha.isoformat()
        }