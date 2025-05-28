from app import db

class DetallesPedido(db.Model):
    __tablename__ = 'detalles_pedido'
    
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    notas = db.Column(db.String(255), nullable=True)    
    
    # Relación con el pedido
    #pedido = db.relationship('Order', backref='detalles', lazy=True)
    
    # Relación con el producto
    #producto = db.relationship('Product', backref='detalles', lazy=True)
    