from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.product import Producto
from app.schemas.product import ProductSchema
from app.services.product_service import ProductService
from app.utils.decorators import admin_required

# Crear el blueprint
bp = Blueprint('products', __name__, url_prefix='/api/products')
product_service = ProductService()

# Obtener todos los productos
@bp.route('', methods=['GET'])
def get_products():
    """Obtener lista de productos con filtros opcionales"""
    # Parámetros de consulta opcionales
    category_id = request.args.get('category_id', type=int)
    disponible = request.args.get('disponible', type=bool, default=None)
    destacado = request.args.get('destacado', type=bool, default=None)
    
    products = product_service.get_products(
        category_id=category_id,
        disponible=disponible,
        destacado=destacado
    )
    
    product_schema = ProductSchema(many=True)
    return jsonify(product_schema.dump(products)), 200

# Obtener un producto por ID
@bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Obtener detalles de un producto específico"""
    product = product_service.get_product_by_id(product_id)
    if not product:
        return jsonify({'message': 'Producto no encontrado'}), 404
    
    product_schema = ProductSchema()
    return jsonify(product_schema.dump(product)), 200

# Crear un nuevo producto (solo admin)
@bp.route('', methods=['POST'])
@jwt_required()
@admin_required
def create_product():
    """Crear un nuevo producto"""
    data = request.get_json()
    
    product_schema = ProductSchema()
    try:
        # Validar datos de entrada
        validated_data = product_schema.load(data)
        product = product_service.create_product(validated_data)
        return jsonify(product_schema.dump(product)), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 400

# Actualizar un producto existente (solo admin)
@bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_product(product_id):
    """Actualizar un producto existente"""
    data = request.get_json()
    
    product = product_service.get_product_by_id(product_id)
    if not product:
        return jsonify({'message': 'Producto no encontrado'}), 404
    
    product_schema = ProductSchema()
    try:
        # Validar datos de entrada
        validated_data = product_schema.load(data, partial=True)
        updated_product = product_service.update_product(product_id, validated_data)
        return jsonify(product_schema.dump(updated_product)), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 400

# Eliminar un producto (solo admin)
@bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_product(product_id):
    """Eliminar un producto"""
    product = product_service.get_product_by_id(product_id)
    if not product:
        return jsonify({'message': 'Producto no encontrado'}), 404
    
    product_service.delete_product(product_id)
    return jsonify({'message': 'Producto eliminado correctamente'}), 200

# Gestionar opciones adicionales de un producto
@bp.route('/<int:product_id>/options', methods=['GET'])
def get_product_options(product_id):
    """Obtener opciones adicionales para un producto"""
    options = product_service.get_product_options(product_id)
    return jsonify(options), 200
    
@bp.route('/<int:product_id>/options', methods=['POST'])
@jwt_required()
@admin_required
def add_product_option(product_id):
    """Añadir una opción a un producto"""
    data = request.get_json()
    try:
        new_option = product_service.add_product_option(product_id, data)
        return jsonify(new_option), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 400