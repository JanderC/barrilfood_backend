from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.category import Categoria
from app.schemas.category import CategorySchema
from app.services.categorias_services import CategoryService
from app.utils.decorators import admin_required

# Crear el blueprint
bp = Blueprint('categories', __name__, url_prefix='/api/categories')
category_service = CategoryService()  # Cambiar nombre del servicio

# Obtener todas las categorías
@bp.route('', methods=['GET'])
def get_categories():
    """Obtener lista de categorías de productos"""
    # Filtrar solo categorías activas por defecto
    show_inactive = request.args.get('show_inactive', type=bool, default=False)
    
    categories = category_service.get_categories(show_inactive=show_inactive)
    category_schema = CategorySchema(many=True)
    return jsonify(category_schema.dump(categories)), 200

# Obtener una categoría por ID
@bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """Obtener detalles de una categoría específica"""
    category = category_service.get_category_by_id(category_id)
    if not category:
        return jsonify({'message': 'Categoría no encontrada'}), 404
    
    category_schema = CategorySchema()
    return jsonify(category_schema.dump(category)), 200

# Crear una nueva categoría (solo admin)
@bp.route('', methods=['POST'])
@jwt_required()
@admin_required
def create_category():
    """Crear una nueva categoría de productos"""
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'No se enviaron datos'}), 400
    
    category_schema = CategorySchema()
    try:
        # Validar datos de entrada
        validated_data = category_schema.load(data)
        category = category_service.create_category(validated_data)
        return jsonify(category_schema.dump(category)), 201
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        return jsonify({'message': f'Error al crear categoría: {str(e)}'}), 400

# Actualizar una categoría existente (solo admin)
@bp.route('/<int:category_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_category(category_id):
    """Actualizar una categoría existente"""
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'No se enviaron datos'}), 400
    
    category = category_service.get_category_by_id(category_id)
    if not category:
        return jsonify({'message': 'Categoría no encontrada'}), 404
    
    category_schema = CategorySchema()
    try:
        # Validar datos de entrada
        validated_data = category_schema.load(data, partial=True)
        updated_category = category_service.update_category(category_id, validated_data)
        return jsonify(category_schema.dump(updated_category)), 200
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        return jsonify({'message': f'Error al actualizar categoría: {str(e)}'}), 400

# Eliminar una categoría (solo admin)
@bp.route('/<int:category_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_category(category_id):
    """Eliminar una categoría"""
    category = category_service.get_category_by_id(category_id)
    if not category:
        return jsonify({'message': 'Categoría no encontrada'}), 404
    
    try:
        category_service.delete_category(category_id)
        return jsonify({'message': 'Categoría eliminada correctamente'}), 200
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        return jsonify({'message': f'Error al eliminar categoría: {str(e)}'}), 400

# Obtener productos por categoría
@bp.route('/<int:category_id>/products', methods=['GET'])
def get_category_products(category_id):
    """Obtener todos los productos de una categoría específica"""
    products = category_service.get_category_products(category_id)
    if products is None:
        return jsonify({'message': 'Categoría no encontrada'}), 404
    
    from app.schemas.product import ProductSchema
    product_schema = ProductSchema(many=True)
    return jsonify(product_schema.dump(products)), 200

# --- RUTAS ADICIONALES ---

# Desactivar una categoría (alternativa a eliminar)
@bp.route('/<int:category_id>/deactivate', methods=['PUT'])
@jwt_required()
@admin_required
def deactivate_category(category_id):
    """Desactivar una categoría"""
    category = category_service.deactivate_category(category_id)
    if not category:
        return jsonify({'message': 'Categoría no encontrada'}), 404
    
    category_schema = CategorySchema()
    return jsonify({
        'message': 'Categoría desactivada correctamente',
        'categoria': category_schema.dump(category)
    }), 200

# Activar una categoría
@bp.route('/<int:category_id>/activate', methods=['PUT'])
@jwt_required()
@admin_required
def activate_category(category_id):
    """Activar una categoría"""
    category = category_service.activate_category(category_id)
    if not category:
        return jsonify({'message': 'Categoría no encontrada'}), 404
    
    category_schema = CategorySchema()
    return jsonify({
        'message': 'Categoría activada correctamente',
        'categoria': category_schema.dump(category)
    }), 200

# Obtener estadísticas de una categoría
@bp.route('/<int:category_id>/stats', methods=['GET'])
def get_category_statistics(category_id):
    """Obtener estadísticas de una categoría"""
    stats = category_service.get_category_statistics(category_id)
    if not stats:
        return jsonify({'message': 'Categoría no encontrada'}), 404
    
    category_schema = CategorySchema()
    return jsonify({
        'categoria': category_schema.dump(stats['categoria']),
        'estadisticas': {
            'total_productos': stats['total_productos'],
            'productos_disponibles': stats['productos_disponibles'],
            'productos_destacados': stats['productos_destacados']
        }
    }), 200

# Buscar categorías
@bp.route('/search', methods=['GET'])
def search_categories():
    """Buscar categorías por nombre o descripción"""
    search_term = request.args.get('q', '')
    if not search_term:
        return jsonify({'message': 'Se requiere un término de búsqueda'}), 400
    
    categories = category_service.search_categories(search_term)
    category_schema = CategorySchema(many=True)
    return jsonify(category_schema.dump(categories)), 200

# Obtener categorías con productos disponibles
@bp.route('/with-products', methods=['GET'])
def get_categories_with_products():
    """Obtener solo las categorías activas que tienen productos disponibles"""
    categories = category_service.get_active_categories_with_products()
    category_schema = CategorySchema(many=True)
    return jsonify(category_schema.dump(categories)), 200