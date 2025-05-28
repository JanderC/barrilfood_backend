# app/services/inventory_service.py
from app.models.product import Producto, OpcionProducto
from app.models.inventory import Inventario
from app import db
from sqlalchemy.exc import SQLAlchemyError

class InventoryService:
    def __init__(self):
        pass
    
    def ingresar_producto(self, product_data, options_data=None, inventory_data=None):
        """
        Ingresa un nuevo producto con sus opciones e inventario si se proporcionan
        
        Args:
            product_data (dict): Datos del producto
            options_data (list, optional): Lista de opciones del producto
            inventory_data (dict, optional): Datos de inventario
            
        Returns:
            dict: Objeto producto con sus relaciones
            
        Raises:
            Exception: Si ocurre algún error durante el proceso
        """
        try:
            # Iniciar transacción
            db.session.begin_nested()
            
            # Crear el producto
            new_product = Producto(**product_data)
            db.session.add(new_product)
            db.session.flush()  # Para obtener el ID generado
            
            # Agregar opciones si existen
            if options_data:
                for option in options_data:
                    option['producto_id'] = new_product.id
                    new_option = OpcionProducto(**option)
                    db.session.add(new_option)
            
            # Agregar inventario si existe
            if inventory_data:
                inventory_data['producto_id'] = new_product.id
                inventory = Inventario(**inventory_data)
                db.session.add(inventory)
            
            # Confirmar transacción
            db.session.commit()
            
            # Construir respuesta
            result = new_product.to_dict(include_options=True)
            if inventory_data:
                result['inventario'] = {
                    'cantidad': inventory.cantidad,
                    'cantidad_minima': inventory.cantidad_minima,
                    'ultima_actualizacion': inventory.ultima_actualizacion.isoformat() if inventory.ultima_actualizacion else None
                }
            
            return result
            
        except SQLAlchemyError as e:
            # Revertir en caso de error
            db.session.rollback()
            raise Exception(f"Error al ingresar producto: {str(e)}")
            
    def actualizar_inventario(self, product_id, cantidad):
        """
        Actualiza la cantidad en inventario de un producto
        
        Args:
            product_id (int): ID del producto
            cantidad (int): Nueva cantidad
            
        Returns:
            Inventario: Objeto inventario actualizado
        """
        inventario = Inventario.query.filter_by(producto_id=product_id).first()
        
        if not inventario:
            # Si no existe inventario para este producto, lo creamos
            inventario = Inventario(producto_id=product_id, cantidad=cantidad)
            db.session.add(inventario)
        else:
            inventario.cantidad = cantidad
            
        db.session.commit()
        return inventario
        
    def obtener_inventario(self, product_id=None):
        """
        Obtiene información de inventario
        
        Args:
            product_id (int, optional): ID del producto para filtrar
            
        Returns:
            list: Lista de inventarios
        """
        query = Inventario.query
        if product_id:
            query = query.filter_by(producto_id=product_id)
            
        return query.all()