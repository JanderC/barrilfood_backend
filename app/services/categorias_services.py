# app/services/category_service.py
from app.models.category import Categoria
from app.models.product import Producto
from app import db

class CategoryService:
    def __init__(self):
        pass

    def get_categories(self, show_inactive=False):
        """Obtener lista de categorías de productos"""
        query = Categoria.query
        if not show_inactive:
            query = query.filter_by(activo=True)
        return query.all()

    def get_category_by_id(self, category_id):
        """Obtener categoría por ID"""
        return Categoria.query.get(category_id)

    def create_category(self, data):
        """Crear una nueva categoría"""
        # Verificar si ya existe una categoría con el mismo nombre
        existing_category = Categoria.query.filter_by(nombre=data.get('nombre')).first()
        if existing_category:
            raise ValueError("Ya existe una categoría con ese nombre")
        
        new_category = Categoria(**data)
        db.session.add(new_category)
        db.session.commit()
        return new_category

    def update_category(self, category_id, data):
        """Actualizar una categoría existente"""
        category = Categoria.query.get(category_id)
        if not category:
            return None
        
        # Verificar si se está actualizando el nombre y ya existe otra categoría con ese nombre
        if 'nombre' in data:
            existing_category = Categoria.query.filter(
                Categoria.nombre == data['nombre'],
                Categoria.id != category_id
            ).first()
            if existing_category:
                raise ValueError("Ya existe otra categoría con ese nombre")
        
        for key, value in data.items():
            setattr(category, key, value)
        db.session.commit()
        return category

    def delete_category(self, category_id):
        """Eliminar una categoría"""
        category = Categoria.query.get(category_id)
        if not category:
            return None
        
        # Verificar si hay productos asociados
        products_count = Producto.query.filter_by(categoria_id=category_id).count()
        if products_count > 0:
            raise ValueError("No se puede eliminar la categoría porque tiene productos asociados")
        
        db.session.delete(category)
        db.session.commit()
        return category

    def deactivate_category(self, category_id):
        """Desactivar una categoría (alternativa a eliminar)"""
        category = Categoria.query.get(category_id)
        if not category:
            return None
        
        category.activo = False
        db.session.commit()
        return category

    def activate_category(self, category_id):
        """Activar una categoría"""
        category = Categoria.query.get(category_id)
        if not category:
            return None
        
        category.activo = True
        db.session.commit()
        return category

    def get_category_products(self, category_id):
        """Obtener todos los productos de una categoría específica"""
        category = Categoria.query.get(category_id)
        if not category:
            return None
        
        return Producto.query.filter_by(categoria_id=category_id).all()

    def get_category_products_count(self, category_id):
        """Obtener el número de productos en una categoría"""
        return Producto.query.filter_by(categoria_id=category_id).count()

    def get_active_categories_with_products(self):
        """Obtener solo las categorías activas que tienen productos"""
        return Categoria.query.join(Producto).filter(
            Categoria.activo == True,
            Producto.disponible == True
        ).distinct().all()

    def search_categories(self, search_term):
        """Buscar categorías por nombre o descripción"""
        search_pattern = f"%{search_term}%"
        return Categoria.query.filter(
            db.or_(
                Categoria.nombre.ilike(search_pattern),
                Categoria.descripcion.ilike(search_pattern)
            )
        ).all()

    def get_category_statistics(self, category_id):
        """Obtener estadísticas de una categoría"""
        category = Categoria.query.get(category_id)
        if not category:
            return None
        
        total_products = Producto.query.filter_by(categoria_id=category_id).count()
        available_products = Producto.query.filter_by(
            categoria_id=category_id, 
            disponible=True
        ).count()
        featured_products = Producto.query.filter_by(
            categoria_id=category_id, 
            destacado=True
        ).count()
        
        return {
            'categoria': category,
            'total_productos': total_products,
            'productos_disponibles': available_products,
            'productos_destacados': featured_products
        }