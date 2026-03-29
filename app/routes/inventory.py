# app/routes/inventory.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.inventory_service import InventoryService
from app.schemas.product import ProductSchema
from app.utils.decorators import admin_required

# Crear el blueprint
bp = Blueprint('inventory', __name__, url_prefix='/api/inventory')
inventory_service = InventoryService()

@bp.route('/ingresar-producto', methods=['POST'])
@jwt_required()
@admin_required
def ingresar_producto():
    """Endpoint para ingresar nuevos productos con inventario"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No se recibieron datos"}), 400
            
        # Extraer datos
        product_data = data.get('producto', {})
        options_data = data.get('opciones', [])
        inventory_data = data.get('inventario', {})
        
        # Validar datos mínimos requeridos
        if not product_data.get('nombre') or product_data.get('precio') is None:
            return jsonify({"error": "El nombre y precio del producto son obligatorios"}), 400
        
        # Procesar el ingreso del producto
        result = inventory_service.ingresar_producto(
            product_data=product_data,
            options_data=options_data,
            inventory_data=inventory_data
        )
        
        return jsonify({
            "mensaje": "Producto ingresado correctamente",
            "producto": result
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@bp.route('/actualizar-stock/<int:product_id>', methods=['PUT'])
@jwt_required()
@admin_required
def actualizar_stock(product_id):
    """Actualizar el stock de un producto existente"""
    try:
        data = request.get_json()
        
        if 'cantidad' not in data:
            return jsonify({"error": "La cantidad es obligatoria"}), 400
            
        cantidad = data['cantidad']
        
        # Actualizar inventario
        inventario = inventory_service.actualizar_inventario(product_id, cantidad)
        
        return jsonify({
            "mensaje": "Inventario actualizado correctamente",
            "inventario": {
                "producto_id": inventario.producto_id,
                "cantidad": inventario.cantidad,
                "cantidad_minima": inventario.cantidad_minima,
                "ultima_actualizacion": inventario.ultima_actualizacion.isoformat() if inventario.ultima_actualizacion else None
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@bp.route('/stock', methods=['GET'])
@jwt_required()
def ver_inventario():
    """Obtener información de inventario"""
    product_id = request.args.get('product_id', type=int)
    
    try:
        inventarios = inventory_service.obtener_inventario(product_id=product_id)
        
        result = []
        for inv in inventarios:
            result.append({
                "producto_id": inv.producto_id,
                "nombre_producto": inv.producto.nombre if inv.producto else "Producto no encontrado",
                "cantidad": inv.cantidad,
                "cantidad_minima": inv.cantidad_minima,
                "ultima_actualizacion": inv.ultima_actualizacion.isoformat() if inv.ultima_actualizacion else None
            })
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400