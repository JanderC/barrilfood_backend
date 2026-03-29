from app import db

class EstadosPedido(db.Model):
    __tablename__ = 'order_status'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255))
    color = db.Column(db.String(50))

    # Aquí puedes agregar más campos relacionados con los estados de los pedidos
