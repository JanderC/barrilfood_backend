# app/services/product_service.py
# Cambiamos la importación de ProductOption a OpcionProducto
from app.models.product import Producto, OpcionProducto
from app import db

class ProductService:
    def __init__(self):
        pass

    def get_products(self, category_id=None, disponible=None, destacado=None):
        """Obtener productos con filtros"""
        query = Producto.query
        if category_id:
            query = query.filter_by(categoria_id=category_id)
        if disponible is not None:
            query = query.filter_by(disponible=disponible)
        if destacado is not None:
            query = query.filter_by(destacado=destacado)
        return query.all()

    def get_product_by_id(self, product_id):
        """Obtener producto por ID"""
        return Producto.query.get(product_id)

    def create_product(self, data):
        """Crear un nuevo producto"""
        new_product = Producto(**data)
        db.session.add(new_product)
        db.session.commit()
        return new_product

    def update_product(self, product_id, data):
        """Actualizar un producto existente"""
        product = Producto.query.get(product_id)
        if not product:
            return None
        for key, value in data.items():
            setattr(product, key, value)
        db.session.commit()
        return product

    def delete_product(self, product_id):
        """Eliminar un producto"""
        product = Producto.query.get(product_id)
        if not product:
            return None
        db.session.delete(product)
        db.session.commit()
        return product

    def get_product_options(self, product_id):
        """Obtener opciones del producto"""
        product = Producto.query.get(product_id)
        if not product:
            return None
        return product.opciones  # Relación con OpcionProducto

    def add_product_option(self, product_id, option_data):
        """Añadir opción al producto"""
        product = Producto.query.get(product_id)
        if not product:
            return None
        # Crear y asociar nueva opción al producto usando OpcionProducto en lugar de ProductOption
        new_option = OpcionProducto(**option_data)
        product.opciones.append(new_option)
        db.session.commit()
        return new_option