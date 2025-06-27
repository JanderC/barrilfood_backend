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
    
    # Validar datos requeridos
    if not data:
        return jsonify({'message': 'No se enviaron datos'}), 400
    
    product_schema = ProductSchema()
    try:
        # Validar datos de entrada (excluir imagen_base64 de la validación del schema)
        product_data = {k: v for k, v in data.items() if k != 'imagen_base64'}
        validated_data = product_schema.load(product_data)
        
        # Agregar imagen_base64 si está presente
        if 'imagen_base64' in data:
            validated_data['imagen_base64'] = data['imagen_base64']
        
        product = product_service.create_product(validated_data)
        return jsonify(product_schema.dump(product)), 201
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        return jsonify({'message': f'Error al crear producto: {str(e)}'}), 400

# Actualizar un producto existente (solo admin)
@bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_product(product_id):
    """Actualizar un producto existente"""
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'No se enviaron datos'}), 400
    
    product = product_service.get_product_by_id(product_id)
    if not product:
        return jsonify({'message': 'Producto no encontrado'}), 404
    
    product_schema = ProductSchema()
    try:
        # Validar datos de entrada (excluir imagen_base64 de la validación del schema)
        product_data = {k: v for k, v in data.items() if k != 'imagen_base64'}
        validated_data = product_schema.load(product_data, partial=True)
        
        # Agregar imagen_base64 si está presente
        if 'imagen_base64' in data:
            validated_data['imagen_base64'] = data['imagen_base64']
            
        updated_product = product_service.update_product(product_id, validated_data)
        return jsonify(product_schema.dump(updated_product)), 200
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        return jsonify({'message': f'Error al actualizar producto: {str(e)}'}), 400

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

# --- NUEVAS RUTAS PARA MANEJO DE IMÁGENES ---

# Actualizar solo la imagen de un producto
@bp.route('/<int:product_id>/image', methods=['PUT'])
@jwt_required()
@admin_required
def update_product_image(product_id):
    """Actualizar solo la imagen de un producto"""
    data = request.get_json()
    
    if not data or 'imagen_base64' not in data:
        return jsonify({'message': 'Se requiere el campo imagen_base64'}), 400
    
    try:
        product, message = product_service.update_product_image(product_id, data['imagen_base64'])
        if not product:
            return jsonify({'message': message}), 404 if 'no encontrado' in message else 400
        
        product_schema = ProductSchema()
        return jsonify({
            'message': message,
            'producto': product_schema.dump(product)
        }), 200
    except Exception as e:
        return jsonify({'message': f'Error al actualizar imagen: {str(e)}'}), 400

# Obtener solo la imagen de un producto
@bp.route('/<int:product_id>/image', methods=['GET'])
def get_product_image(product_id):
    """Obtener solo la imagen de un producto"""
    imagen = product_service.get_product_image(product_id)
    if imagen is None:
        return jsonify({'message': 'Producto no encontrado o sin imagen'}), 404
    
    return jsonify({'imagen_url': imagen}), 200

# Remover la imagen de un producto
@bp.route('/<int:product_id>/image', methods=['DELETE'])
@jwt_required()
@admin_required
def remove_product_image(product_id):
    """Remover la imagen de un producto"""
    try:
        product, message = product_service.remove_product_image(product_id)
        if not product:
            return jsonify({'message': message}), 404
        
        product_schema = ProductSchema()
        return jsonify({
            'message': message,
            'producto': product_schema.dump(product)
        }), 200
    except Exception as e:
        return jsonify({'message': f'Error al remover imagen: {str(e)}'}), 400

# --- RUTAS EXISTENTES PARA OPCIONES ---

# Desactivar un producto (cambiar disponible a False)
@bp.route('/<int:product_id>/deactivate', methods=['PUT'])
@jwt_required()
@admin_required
def deactivate_product(product_id):
    """Desactivar un producto (cambiar disponible a False)"""
    try:
        product, message = product_service.deactivate_product(product_id)
        if not product:
            return jsonify({'message': message}), 404
        
        product_schema = ProductSchema()
        return jsonify({
            'message': message,
            'producto': product_schema.dump(product)
        }), 200
    except Exception as e:
        return jsonify({'message': f'Error al desactivar producto: {str(e)}'}), 400

# Activar un producto (cambiar disponible a True)
@bp.route('/<int:product_id>/activate', methods=['PUT'])
@jwt_required()
@admin_required
def activate_product(product_id):
    """Activar un producto (cambiar disponible a True)"""
    try:
        product, message = product_service.activate_product(product_id)
        if not product:
            return jsonify({'message': message}), 404
        
        product_schema = ProductSchema()
        return jsonify({
            'message': message,
            'producto': product_schema.dump(product)
        }), 200
    except Exception as e:
        return jsonify({'message': f'Error al activar producto: {str(e)}'}), 400

# Alternar estado de disponibilidad de un producto
@bp.route('/<int:product_id>/toggle-availability', methods=['PATCH'])
@jwt_required()
@admin_required
def toggle_product_availability(product_id):
    """Alternar el estado de disponibilidad de un producto"""
    try:
        product, message = product_service.toggle_product_availability(product_id)
        if not product:
            return jsonify({'message': message}), 404
        
        product_schema = ProductSchema()
        return jsonify({
            'message': message,
            'producto': product_schema.dump(product)
        }), 200
    except Exception as e:
        return jsonify({'message': f'Error al cambiar disponibilidad del producto: {str(e)}'}), 400

# Gestionar opciones adicionales de un producto
@bp.route('/<int:product_id>/options', methods=['GET'])
def get_product_options(product_id):
    """Obtener opciones adicionales para un producto"""
    options = product_service.get_product_options(product_id)
    if options is None:
        return jsonify({'message': 'Producto no encontrado'}), 404
    return jsonify([option.to_dict() for option in options]), 200
    
@bp.route('/<int:product_id>/options', methods=['POST'])
@jwt_required()
@admin_required
def add_product_option(product_id):
    """Añadir una opción a un producto"""
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'No se enviaron datos'}), 400
    
    try:
        new_option = product_service.add_product_option(product_id, data)
        if not new_option:
            return jsonify({'message': 'Producto no encontrado'}), 404
        return jsonify(new_option.to_dict()), 201
    except Exception as e:
        return jsonify({'message': f'Error al crear opción: {str(e)}'}), 400
    
    # Desactivar múltiples productos en lote
@bp.route('/bulk/deactivate', methods=['PATCH'])
@jwt_required()
@admin_required
def bulk_deactivate_products():
    """Desactivar múltiples productos en lote"""
    data = request.get_json()
    
    if not data or 'product_ids' not in data:
        return jsonify({'message': 'Se requiere el campo product_ids con una lista de IDs'}), 400
    
    product_ids = data['product_ids']
    if not isinstance(product_ids, list) or not product_ids:
        return jsonify({'message': 'product_ids debe ser una lista no vacía'}), 400
    
    try:
        products, message = product_service.bulk_deactivate_products(product_ids)
        product_schema = ProductSchema(many=True)
        
        return jsonify({
            'message': message,
            'productos_actualizados': product_schema.dump(products),
            'cantidad_actualizados': len(products)
        }), 200
    except Exception as e:
        return jsonify({'message': f'Error al desactivar productos: {str(e)}'}), 400

# Activar múltiples productos en lote
@bp.route('/bulk/activate', methods=['PATCH'])
@jwt_required()
@admin_required
def bulk_activate_products():
    """Activar múltiples productos en lote"""
    data = request.get_json()
    
    if not data or 'product_ids' not in data:
        return jsonify({'message': 'Se requiere el campo product_ids con una lista de IDs'}), 400
    
    product_ids = data['product_ids']
    if not isinstance(product_ids, list) or not product_ids:
        return jsonify({'message': 'product_ids debe ser una lista no vacía'}), 400
    
    try:
        products, message = product_service.bulk_activate_products(product_ids)
        product_schema = ProductSchema(many=True)
        
        return jsonify({
            'message': message,
            'productos_actualizados': product_schema.dump(products),
            'cantidad_actualizados': len(products)
        }), 200
    except Exception as e:
        return jsonify({'message': f'Error al activar productos: {str(e)}'}), 400

# Obtener productos por estado de disponibilidad
@bp.route('/by-availability', methods=['GET'])
def get_products_by_availability():
    """Obtener productos filtrados por disponibilidad"""
    disponible = request.args.get('disponible', type=bool, default=True)
    
    try:
        products = product_service.get_products_by_availability(disponible)
        product_schema = ProductSchema(many=True)
        
        return jsonify({
            'productos': product_schema.dump(products),
            'total': len(products),
            'disponible': disponible
        }), 200
    except Exception as e:
        return jsonify({'message': f'Error al obtener productos: {str(e)}'}), 400