# app/routes/user_orders.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.user_service import UserService
from app.models.user import User
from app import db

bp = Blueprint('user_orders', __name__, url_prefix='/api/user')

user_service = UserService()

@bp.route('/orders', methods=['GET'])
@jwt_required()
def get_my_orders():
    """
    Obtener todos los pedidos del usuario autenticado
    Query params opcionales:
    - estado_id: filtrar por estado
    - fecha_inicio: YYYY-MM-DD
    - fecha_fin: YYYY-MM-DD
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Obtener parámetros de consulta
        estado_id = request.args.get('estado_id', type=int)
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        orders = user_service.get_user_orders(
            usuario_id=current_user_id,
            estado_id=estado_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
        
        # Formatear respuesta
        orders_list = []
        for order in orders:
            orders_list.append({
                'id': str(order.id),
                'fecha_pedido': order.fecha_pedido.isoformat(),
                'estado_id': order.estado_id,
                'subtotal': float(order.subtotal),
                'costo_envio': float(order.costo_envio or 0),
                'descuento': float(order.descuento or 0),
                'total': float(order.total),
                'notas': order.notas,
                'codigo_seguimiento': order.codigo_seguimiento
            })
        
        return jsonify({
            'data': orders_list,
            'total': len(orders_list)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/orders/<order_id>', methods=['GET'])
@jwt_required()
def get_order_details(order_id):
    """
    Obtener detalles completos de un pedido específico
    """
    try:
        current_user_id = get_jwt_identity()
        
        order_details = user_service.get_order_details_with_products(
            order_id=order_id,
            usuario_id=current_user_id
        )
        
        return jsonify({
            'data': order_details
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@bp.route('/orders/<order_id>/take', methods=['POST'])
@jwt_required()
def take_order(order_id):
    """
    Tomar/confirmar un pedido (cambiar estado de pendiente a confirmado)
    """
    try:
        current_user_id = get_jwt_identity()
        
        order = user_service.take_order(
            order_id=order_id,
            usuario_id=current_user_id
        )
        
        return jsonify({
            'message': 'Pedido confirmado exitosamente',
            'data': {
                'id': str(order.id),
                'estado_id': order.estado_id,
                'fecha_pedido': order.fecha_pedido.isoformat(),
                'total': float(order.total)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/orders/<order_id>/status', methods=['PUT'])
@jwt_required()
def update_order_status(order_id):
    """
    Cambiar el estado de un pedido (solo estados permitidos para el usuario)
    Body: {
        "estado_id": 2,
        "notas": "Motivo del cambio (opcional)"
    }
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'estado_id' not in data:
            return jsonify({'error': 'estado_id es requerido'}), 400
        
        nuevo_estado_id = data['estado_id']
        notas = data.get('notas')
        
        order = user_service.update_order_status_by_user(
            order_id=order_id,
            usuario_id=current_user_id,
            nuevo_estado_id=nuevo_estado_id,
            notas=notas
        )
        
        return jsonify({
            'message': 'Estado del pedido actualizado exitosamente',
            'data': {
                'id': str(order.id),
                'estado_id': order.estado_id,
                'fecha_pedido': order.fecha_pedido.isoformat(),
                'total': float(order.total)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/orders/<order_id>/history', methods=['GET'])
@jwt_required()
def get_order_history(order_id):
    """
    Obtener historial de cambios de estado de un pedido
    """
    try:
        current_user_id = get_jwt_identity()
        
        history = user_service.get_order_history(
            order_id=order_id,
            usuario_id=current_user_id
        )
        
        return jsonify({
            'data': history
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """
    Actualizar datos personales del usuario
    Body: {
        "nombre": "Nuevo nombre",
        "apellido": "Nuevo apellido",
        "telefono": "1234567890",
        "email": "nuevo@email.com"
    }
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Datos requeridos'}), 400
        
        user = user_service.update_user_profile(
            usuario_id=current_user_id,
            profile_data=data
        )
        
        return jsonify({
            'message': 'Perfil actualizado exitosamente',
            'data': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """
    Cambiar contraseña del usuario
    Body: {
        "current_password": "contraseña_actual",
        "new_password": "nueva_contraseña"
    }
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'current_password' not in data or 'new_password' not in data:
            return jsonify({'error': 'current_password y new_password son requeridos'}), 400
        
        current_password = data['current_password']
        new_password = data['new_password']
        
        success = user_service.change_password(
            usuario_id=current_user_id,
            current_password=current_password,
            new_password=new_password
        )
        
        if success:
            return jsonify({
                'message': 'Contraseña cambiada exitosamente'
            }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """
    Obtener información del perfil del usuario autenticado
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        return jsonify({
            'data': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500