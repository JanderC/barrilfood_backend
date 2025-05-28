from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.order import OpcionSeleccionada, Pedido, HistorialEstadoPedido  
from app.schemas.order import OrderSchema, OrderCreateSchema, OrderDetailSchema
from app.services.order_service import OrderService
from app.utils.decorators import admin_required, employee_required

# Crear el blueprint
bp = Blueprint('orders', __name__, url_prefix='/api/orders')
order_service = OrderService()

# Obtener todos los pedidos (admin/empleado)
@bp.route('', methods=['GET'])
@jwt_required()
def get_orders():
    """Obtener lista de pedidos con filtros opcionales"""
    user_id = get_jwt_identity()
    
    # Parámetros de filtro
    estado_id = request.args.get('estado_id', type=int)
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
    # Verificar si el usuario puede ver todos los pedidos o solo los suyos
    from app.services.auth_service import AuthService
    auth_service = AuthService()
    user_role = auth_service.get_user_role(user_id)
    
    if user_role in ['administrador', 'empleado', 'repartidor']:
        # Administradores, empleados y repartidores pueden ver todos los pedidos
        orders = order_service.get_orders(
            estado_id=estado_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            repartidor_id=request.args.get('repartidor_id') if user_role in ['administrador', 'empleado'] else None
        )
    else:
        # Clientes solo pueden ver sus propios pedidos
        orders = order_service.get_orders(
            usuario_id=user_id,
            estado_id=estado_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
    
    order_schema = OrderSchema(many=True)
    return jsonify(order_schema.dump(orders)), 200

# Obtener un pedido por ID
@bp.route('/<uuid:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    """Obtener detalles de un pedido específico"""
    user_id = get_jwt_identity()
    
    # Verificar si el usuario puede ver este pedido
    from app.services.auth_service import AuthService
    auth_service = AuthService()
    user_role = auth_service.get_user_role(user_id)
    
    order = order_service.get_order_by_id(order_id)
    if not order:
        return jsonify({'message': 'Pedido no encontrado'}), 404
    
    # Verificar permisos de acceso
    if user_role not in ['administrador', 'empleado', 'repartidor'] and str(order.usuario_id) != user_id:
        return jsonify({'message': 'No tienes permiso para ver este pedido'}), 403
    
    order_schema = OrderSchema()
    return jsonify(order_schema.dump(order)), 200

# Crear un nuevo pedido
@bp.route('', methods=['POST'])
@jwt_required()
def create_order():
    """Crear un nuevo pedido"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Asignar el ID del usuario al pedido
    data['usuario_id'] = user_id
    
    order_create_schema = OrderCreateSchema()
    try:
        # Validar datos de entrada
        validated_data = order_create_schema.load(data)
        order = order_service.create_order(validated_data)
        
        order_schema = OrderSchema()
        return jsonify(order_schema.dump(order)), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 400

# Actualizar estado de un pedido (admin/empleado)
@bp.route('/<uuid:order_id>/status', methods=['PUT'])
@jwt_required()
@employee_required
def update_order_status(order_id):
    """Actualizar el estado de un pedido"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if 'estado_id' not in data:
        return jsonify({'message': 'Se requiere el ID del estado'}), 400
    
    order = order_service.get_order_by_id(order_id)
    if not order:
        return jsonify({'message': 'Pedido no encontrado'}), 404
    
    try:
        updated_order = order_service.update_order_status(
            order_id=order_id,
            estado_id=data['estado_id'],
            usuario_id=user_id,
            notas=data.get('notas')
        )
        
        order_schema = OrderSchema()
        return jsonify(order_schema.dump(updated_order)), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 400

# Asignar repartidor a un pedido (admin/empleado)
@bp.route('/<uuid:order_id>/delivery', methods=['PUT'])
@jwt_required()
@employee_required
def assign_delivery(order_id):
    """Asignar un repartidor a un pedido"""
    data = request.get_json()
    
    if 'repartidor_id' not in data:
        return jsonify({'message': 'Se requiere el ID del repartidor'}), 400
    
    order = order_service.get_order_by_id(order_id)
    if not order:
        return jsonify({'message': 'Pedido no encontrado'}), 404
    
    try:
        updated_order = order_service.assign_delivery(
            order_id=order_id,
            repartidor_id=data['repartidor_id']
        )
        
        order_schema = OrderSchema()
        return jsonify(order_schema.dump(updated_order)), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 400

# Cancelar un pedido
@bp.route('/<uuid:order_id>/cancel', methods=['PUT'])
@jwt_required()
def cancel_order(order_id):
    """Cancelar un pedido"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    order = order_service.get_order_by_id(order_id)
    if not order:
        return jsonify({'message': 'Pedido no encontrado'}), 404
    
    # Verificar permisos para cancelar
    from app.services.auth_service import AuthService
    auth_service = AuthService()
    user_role = auth_service.get_user_role(user_id)
    
    # Solo el cliente que hizo el pedido o un admin/empleado puede cancelarlo
    if user_role not in ['administrador', 'empleado'] and str(order.usuario_id) != user_id:
        return jsonify({'message': 'No tienes permiso para cancelar este pedido'}), 403
    
    # Solo se pueden cancelar pedidos en ciertos estados
    if order.estado_id not in [1, 2]:  # pendiente o confirmado
        return jsonify({'message': 'Este pedido ya no puede ser cancelado'}), 400
    
    try:
        canceled_order = order_service.cancel_order(
            order_id=order_id,
            usuario_id=user_id,
            motivo=data.get('motivo', '')
        )
        
        order_schema = OrderSchema()
        return jsonify(order_schema.dump(canceled_order)), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 400

# Obtener historial de estados de un pedido
@bp.route('/<uuid:order_id>/history', methods=['GET'])
@jwt_required()
def get_order_history(order_id):
    """Obtener historial de estados de un pedido"""
    user_id = get_jwt_identity()
    
    order = order_service.get_order_by_id(order_id)
    if not order:
        return jsonify({'message': 'Pedido no encontrado'}), 404
    
    # Verificar permisos de acceso
    from app.services.auth_service import AuthService
    auth_service = AuthService()
    user_role = auth_service.get_user_role(user_id)
    
    if user_role not in ['administrador', 'empleado', 'repartidor'] and str(order.usuario_id) != user_id:
        return jsonify({'message': 'No tienes permiso para ver este pedido'}), 403
    
    history = order_service.get_order_history(order_id)
    return jsonify(history), 200

# Añadir valoración a un pedido completado
@bp.route('/<uuid:order_id>/review', methods=['POST'])
@jwt_required()
def add_order_review(order_id):
    """Añadir valoración a un pedido completado"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    order = order_service.get_order_by_id(order_id)
    if not order:
        return jsonify({'message': 'Pedido no encontrado'}), 404
    
    # Solo el cliente que hizo el pedido puede valorarlo
    if str(order.usuario_id) != user_id:
        return jsonify({'message': 'No tienes permiso para valorar este pedido'}), 403
    
    # Solo se pueden valorar pedidos entregados
    if order.estado_id != 6:  # entregado
        return jsonify({'message': 'Solo puedes valorar pedidos que hayan sido entregados'}), 400
    
    try:
        review = order_service.add_review(
            pedido_id=order_id,
            usuario_id=user_id,
            producto_id=data.get('producto_id'),
            calificacion=data.get('calificacion'),
            comentario=data.get('comentario', '')
        )
        
        return jsonify(review), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 400