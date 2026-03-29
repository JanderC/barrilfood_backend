from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.category import Categoria
from app.schemas.category import CategorySchema
from app.services.product_service import ProductService
from app.utils.decorators import admin_required

# Crear el blueprint
bp = Blueprint('categories', __name__, url_prefix='/api/categories')
product_service = ProductService()

# Obtener todas las categorías
@bp.route('', methods=['GET'])
def get_categories():
    """Obtener lista de categorías de productos"""
    # Filtrar solo categorías activas por defecto
    show_inactive = request.args.get('show_inactive', type=bool, default=False)
    
    categories = product_service.get_categories(show_inactive=show_inactive)
    category_schema = CategorySchema(many=True)
    return jsonify(category_schema.dump(categories)), 200

# Obtener una categoría por ID
@bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """Obtener detalles de una categoría específica"""
    category = product_service.get_category_by_id(category_id)
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
    
    category_schema = CategorySchema()
    try:
        # Validar datos de entrada
        validated_data = category_schema.load(data)
        category = product_service.create_category(validated_data)
        return jsonify(category_schema.dump(category)), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 400

# Actualizar una categoría existente (solo admin)
@bp.route('/<int:category_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_category(category_id):
    """Actualizar una categoría existente"""
    data = request.get_json()
    
    category = product_service.get_category_by_id(category_id)
    if not category:
        return jsonify({'message': 'Categoría no encontrada'}), 404
    
    category_schema = CategorySchema()
    try:
        # Validar datos de entrada
        validated_data = category_schema.load(data, partial=True)
        updated_category = product_service.update_category(category_id, validated_data)
        return jsonify(category_schema.dump(updated_category)), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 400

# Eliminar una categoría (solo admin)
@bp.route('/<int:category_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_category(category_id):
    """Eliminar una categoría"""
    category = product_service.get_category_by_id(category_id)
    if not category:
        return jsonify({'message': 'Categoría no encontrada'}), 404
    
    # Verificar si hay productos en esta categoría
    products = product_service.get_products(category_id=category_id)
    if products:
        return jsonify({
            'message': 'No se puede eliminar la categoría porque tiene productos asociados. Considere desactivarla en su lugar.'
        }), 400
    
    product_service.delete_category(category_id)
    return jsonify({'message': 'Categoría eliminada correctamente'}), 200

# Obtener productos por categoría
@bp.route('/<int:category_id>/products', methods=['GET'])
def get_category_products(category_id):
    """Obtener todos los productos de una categoría específica"""
    category = product_service.get_category_by_id(category_id)
    if not category:
        return jsonify({'message': 'Categoría no encontrada'}), 404
    
    products = product_service.get_products(category_id=category_id)
    from app.schemas.product import ProductSchema
    product_schema = ProductSchema(many=True)
    return jsonify(product_schema.dump(products)), 200