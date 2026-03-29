from app.models import db
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime

class Notificacion(db.Model):
    __tablename__ = 'notificaciones'
    __table_args__ = {'schema': 'barrilfood'}
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(UUID(as_uuid=True), db.ForeignKey('barrilfood.usuarios.id'))
    titulo = db.Column(db.String(100), nullable=False)
    mensaje = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(20))  # sistema, pedido, promoción, etc.
    leida = db.Column(db.Boolean, default=False)
    fecha = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    data = db.Column(JSONB)  # datos adicionales en formato JSON
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Notificacion {self.id} para {self.usuario_id}>'
    
    def marcar_como_leida(self):
        self.leida = True
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'mensaje': self.mensaje,
            'tipo': self.tipo,
            'leida': self.leida,
            'fecha': self.fecha.isoformat(),
            'data': self.data
        }