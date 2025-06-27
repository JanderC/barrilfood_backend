# app/services/product_service.py
import base64
import re
from app.models.product import Producto, OpcionProducto
from app import db

class ProductService:
    def __init__(self):
        pass

    def _validate_base64_image(self, base64_string):
        """Validar que el string base64 sea una imagen válida"""
        try:
            # Verificar formato data:image/[tipo];base64,[datos]
            if not base64_string.startswith('data:image/'):
                return False, "El formato debe ser data:image/[tipo];base64,[datos]"
            
            # Extraer el tipo de imagen y los datos
            header, data = base64_string.split(',', 1)
            image_type = header.split('/')[1].split(';')[0]
            
            # Validar tipos de imagen permitidos
            allowed_types = ['jpeg', 'jpg', 'png', 'gif', 'webp']
            if image_type.lower() not in allowed_types:
                return False, f"Tipo de imagen no permitido. Tipos válidos: {', '.join(allowed_types)}"
            
            # Validar que los datos base64 sean válidos
            try:
                decoded = base64.b64decode(data)
                # Verificar tamaño (ejemplo: máximo 5MB)
                if len(decoded) > 5 * 1024 * 1024:
                    return False, "La imagen no puede superar los 5MB"
            except Exception:
                return False, "Los datos base64 no son válidos"
            
            return True, "Imagen válida"
            
        except Exception as e:
            return False, f"Error al validar la imagen: {str(e)}"

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
        # Validar imagen si está presente
        if 'imagen_base64' in data:
            is_valid, message = self._validate_base64_image(data['imagen_base64'])
            if not is_valid:
                raise ValueError(f"Error en la imagen: {message}")
            
            # Guardar la imagen base64 en imagen_url
            data['imagen_url'] = data['imagen_base64']
            del data['imagen_base64']  # Remover el campo temporal
        
        new_product = Producto(**data)
        db.session.add(new_product)
        db.session.commit()
        return new_product

    def update_product(self, product_id, data):
        """Actualizar un producto existente"""
        product = Producto.query.get(product_id)
        if not product:
            return None
        
        # Validar imagen si está presente en la actualización
        if 'imagen_base64' in data:
            is_valid, message = self._validate_base64_image(data['imagen_base64'])
            if not is_valid:
                raise ValueError(f"Error en la imagen: {message}")
            
            # Actualizar la imagen base64 en imagen_url
            data['imagen_url'] = data['imagen_base64']
            del data['imagen_base64']  # Remover el campo temporal
        
        for key, value in data.items():
            setattr(product, key, value)
        db.session.commit()
        return product

    def update_product_image(self, product_id, base64_image):
        """Actualizar solo la imagen de un producto"""
        product = Producto.query.get(product_id)
        if not product:
            return None, "Producto no encontrado"
        
        # Validar imagen
        is_valid, message = self._validate_base64_image(base64_image)
        if not is_valid:
            return None, message
        
        # Actualizar imagen
        product.imagen_url = base64_image
        db.session.commit()
        return product, "Imagen actualizada correctamente"

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

    def get_product_image(self, product_id):
        """Obtener solo la imagen de un producto"""
        product = Producto.query.get(product_id)
        if not product:
            return None
        return product.imagen_url

    def remove_product_image(self, product_id):
        """Remover la imagen de un producto"""
        product = Producto.query.get(product_id)
        if not product:
            return None, "Producto no encontrado"
        
        product.imagen_url = None
        db.session.commit()
        return product, "Imagen removida correctamente"
    
    # Agregar estos métodos al final de la clase ProductService en product_service.py

    def deactivate_product(self, product_id):
        """Desactivar un producto (cambiar disponible a False)"""
        product = Producto.query.get(product_id)
        if not product:
            return None, "Producto no encontrado"
        
        if not product.disponible:
            return product, "El producto ya estaba desactivado"
        
        product.disponible = False
        db.session.commit()
        return product, "Producto desactivado correctamente"

    def activate_product(self, product_id):
        """Activar un producto (cambiar disponible a True)"""
        product = Producto.query.get(product_id)
        if not product:
            return None, "Producto no encontrado"
        
        if product.disponible:
            return product, "El producto ya estaba activado"
        
        product.disponible = True
        db.session.commit()
        return product, "Producto activado correctamente"

    def toggle_product_availability(self, product_id):
        """Alternar el estado de disponibilidad de un producto"""
        product = Producto.query.get(product_id)
        if not product:
            return None, "Producto no encontrado"
        
        # Cambiar el estado actual
        product.disponible = not product.disponible
        db.session.commit()
        
        status = "activado" if product.disponible else "desactivado"
        return product, f"Producto {status} correctamente"

    def get_products_by_availability(self, disponible=True):
        """Obtener productos por estado de disponibilidad"""
        return Producto.query.filter_by(disponible=disponible).all()

    def bulk_deactivate_products(self, product_ids):
        """Desactivar múltiples productos en lote"""
        if not product_ids:
            return [], "No se proporcionaron IDs de productos"
        
        products = Producto.query.filter(Producto.id.in_(product_ids)).all()
        if not products:
            return [], "No se encontraron productos con los IDs proporcionados"
        
        updated_products = []
        for product in products:
            if product.disponible:  # Solo actualizar si está disponible
                product.disponible = False
                updated_products.append(product)
        
        if updated_products:
            db.session.commit()
            return updated_products, f"{len(updated_products)} productos desactivados correctamente"
        else:
            return [], "Todos los productos ya estaban desactivados"

    def bulk_activate_products(self, product_ids):
        """Activar múltiples productos en lote"""
        if not product_ids:
            return [], "No se proporcionaron IDs de productos"
        
        products = Producto.query.filter(Producto.id.in_(product_ids)).all()
        if not products:
            return [], "No se encontraron productos con los IDs proporcionados"
        
        updated_products = []
        for product in products:
            if not product.disponible:  # Solo actualizar si no está disponible
                product.disponible = True
                updated_products.append(product)
        
        if updated_products:
            db.session.commit()
            return updated_products, f"{len(updated_products)} productos activados correctamente"
        else:
            return [], "Todos los productos ya estaban activados"