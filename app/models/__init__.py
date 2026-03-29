# app/models/__init__.py
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

def init_app(app):
    db.init_app(app)
    
    # Importar todos los modelos para asegurar que SQLAlchemy los reconozca
    from app.models.notification import Notificacion
    from app.models.user import User, Role
    from app.models.address import Direccion
    from app.models.category import Categoria
    from app.models.product import Producto, OpcionProducto
    from app.models.inventory import Inventario
    from app.models.order import (
        EstadoPedido, MetodoPago, Pedido, DetallePedido,
        OpcionSeleccionada, HistorialEstadoPedido
    )
    from app.models.review import Valoracion
    from app.models.promotion import Promocion
    from app.models.configuration import Configuracion
    
    # Devolver instancia de la base de datos
    return db