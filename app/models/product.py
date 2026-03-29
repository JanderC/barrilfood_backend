# app/models/product.py
from app.models import db
from datetime import datetime

class Producto(db.Model):
    __tablename__ = 'productos'
    __table_args__ = {'schema': 'barrilfood'}
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    imagen_url = db.Column(db.String(255))
    tiempo_preparacion = db.Column(db.Integer)  # en minutos
    categoria_id = db.Column(db.Integer, db.ForeignKey('barrilfood.categorias.id'))
    disponible = db.Column(db.Boolean, default=True)
    destacado = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    opciones = db.relationship('OpcionProducto', backref='producto', lazy='dynamic', cascade='all, delete-orphan')
    detalles_pedido = db.relationship('DetallePedido', backref='producto', lazy='dynamic')
    valoraciones = db.relationship('Valoracion', backref='producto', lazy='dynamic')
    
    def __repr__(self):
        return f'<Producto {self.nombre}>'
    
    def calificacion_promedio(self):
        valoraciones = self.valoraciones.all()
        if not valoraciones:
            return 0
        return sum(v.calificacion for v in valoraciones) / len(valoraciones)
    
    def to_dict(self, include_options=False):
        result = {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'precio': float(self.precio),
            'imagen_url': self.imagen_url,
            'tiempo_preparacion': self.tiempo_preparacion,
            'categoria_id': self.categoria_id,
            'disponible': self.disponible,
            'destacado': self.destacado,
            'calificacion': self.calificacion_promedio()
        }
        
        if include_options:
            result['opciones'] = [opcion.to_dict() for opcion in self.opciones]
            
        return result

class OpcionProducto(db.Model):
    __tablename__ = 'opciones_producto'
    __table_args__ = {'schema': 'barrilfood'}
    
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('barrilfood.productos.id', ondelete='CASCADE'))
    nombre = db.Column(db.String(100), nullable=False)
    # ELIMINÉ categoria_id porque no existe en la tabla real
    precio_adicional = db.Column(db.Numeric(10, 2), default=0)
    disponible = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación con opciones seleccionadas
    opciones_seleccionadas = db.relationship('OpcionSeleccionada', backref='opcion', lazy='dynamic')
    
    def __repr__(self):
        return f'<OpcionProducto {self.nombre} para {self.producto_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'precio_adicional': float(self.precio_adicional),
            'disponible': self.disponible
        }
    
    # Método para compatibilidad con ProductOption
    def get_value(self):
        """Método para mantener compatibilidad con código que podría usar ProductOption"""
        return self.nombre
    
# Importar al final para evitar importación circular
from app.models.inventory import Inventario

# Definir la relación después de que ambas clases estén disponibles
Producto.inventario = db.relationship('Inventario', backref='producto', uselist=False, cascade='all, delete-orphan')