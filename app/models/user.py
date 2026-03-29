# app/models/user.py
from app.models import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Role(db.Model):
    __tablename__ = 'roles'
    __table_args__ = {'schema': 'barrilfood'}
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación con la tabla usuarios
    usuarios = db.relationship('User', backref='role', lazy='dynamic')
    
    def __repr__(self):
        return f'<Role {self.nombre}>'

class User(db.Model):
    __tablename__ = 'usuarios'
    __table_args__ = {'schema': 'barrilfood'}
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    rol_id = db.Column(db.Integer, db.ForeignKey('barrilfood.roles.id'))
    activo = db.Column(db.Boolean, default=True)
    fecha_registro = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    ultimo_acceso = db.Column(db.TIMESTAMP)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    direcciones = db.relationship('Direccion', backref='usuario', lazy='dynamic', cascade='all, delete-orphan')
    pedidos_cliente = db.relationship('Pedido', backref='cliente', lazy='dynamic', foreign_keys='Pedido.usuario_id')
    pedidos_repartidor = db.relationship('Pedido', backref='repartidor', lazy='dynamic', foreign_keys='Pedido.repartidor_id')
    valoraciones = db.relationship('Valoracion', backref='usuario', lazy='dynamic')
    historial_estados = db.relationship('HistorialEstadoPedido', backref='usuario', lazy='dynamic')

    def __init__(self, email, password, nombre, apellido, telefono, rol_id):
        self.email = email
        self.set_password(password)
        self.nombre = nombre
        self.apellido = apellido
        self.telefono = telefono
        self.rol_id = rol_id
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"
    
    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email).first()
    
    def to_dict(self):
        """
        Convertir el objeto usuario a un diccionario para la API
        """
        return {
            'id': str(self.id),
            'email': self.email,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'nombre_completo': self.nombre_completo,
            'telefono': self.telefono,
            'rol_id': self.rol_id,
            'activo': self.activo,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None,
            'ultimo_acceso': self.ultimo_acceso.isoformat() if self.ultimo_acceso else None
        }
    
    def __repr__(self):
        return f'<User {self.email}>'