from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.delivery_service import DeliveryService
from app.schemas.order import OrderSchema
from app.utils.decorators import delivery_required, admin_required

# Crear el blueprint
bp = Blueprint('delivery', __name__, url_prefix='/api/delivery')
delivery_service = DeliveryService()

# Obtener pedidos asignados a un repartidor
@bp.route('/assignments', methods=['GET'])
@jwt_required()
@delivery_required
def get_delivery_assignments():
    """Obtener pedidos asignados al repartidor actual"""
    user_id = get_jwt_identity()
    
    # Filtrar por estado
    estado_id = request.args.get('estado_id', type=int)
    
    # Obtener todos los pedidos para admins/empleados o solo los asignados para repartidores
    from app.services.auth_service import AuthService
    auth_service = AuthService()
    user_role = auth_service.get_user_role(user_id)
    
    if user_role in ['administrador', 'empleado']:
        # Admins y empleados pueden ver todos los pedidos en reparto
        repartidor_id = request.args.get('repartidor_id')
        orders = delivery_service.get_delivery_orders(
            repartidor_id=repartidor_id,
            estado_id=estado_id
        )
    else:
        # Repartidores ven solo sus pedidos asignados
        orders = delivery_service.get_delivery_orders(
            repartidor_id=user_id,
            estado_id=estado_id
        )
    
    order_schema = OrderSchema(many=True)
    return jsonify(order_schema.dump(orders)), 200

# Aceptar un pedido asignado (repartidor)
@bp.route('/orders/<uuid:order_id>/accept', methods=['PUT'])
@jwt_required()
@delivery_required
def accept_delivery(order_id):
    """Repartidor acepta un pedido asignado"""
    user_id = get_jwt_identity()
    
    try:
        order = delivery_service.accept_delivery(
            order_id=order_id,
            repartidor_id=user_id
        )
        
        order_schema = OrderSchema()
        return jsonify(order_schema.dump(order)), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 400

# Iniciar entrega de un pedido
@bp.route('/orders/<uuid:order_id>/start', methods=['PUT'])
@jwt_required()
@delivery_required
def start_delivery(order_id):
    """Repartidor inicia la entrega de un pedido"""
    user_id = get_jwt_identity()
    
    try:
        order = delivery_service.start_delivery(
            order_id=order_id,
            repartidor_id=user_id
        )
        
        order_schema = OrderSchema()
        return jsonify(order_schema.dump(order)), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 400

# Completar entrega de un pedido
@bp.route('/orders/<uuid:order_id>/complete', methods=['PUT'])
@jwt_required()
@delivery_required
def complete_delivery(order_id):
    """Repartidor completa la entrega de un pedido"""
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    
    try:
        order = delivery_service.complete_delivery(
            order_id=order_id,
            repartidor_id=user_id,
            notas=data.get('notas', '')
        )
        
        order_schema = OrderSchema()
        return jsonify(order_schema.dump(order)), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 400

# Reportar problema con entrega
@bp.route('/orders/<uuid:order_id>/issue', methods=['POST'])
@jwt_required()
@delivery_required
def report_delivery_issue(order_id):
    """Reportar un problema durante la entrega"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data.get('descripcion'):
        return jsonify({'message': 'Se requiere una descripción del problema'}), 400
    
    try:
        issue = delivery_service.report_delivery_issue(
            order_id=order_id,
            repartidor_id=user_id,
            descripcion=data.get('descripcion'),
            tipo_problema=data.get('tipo_problema', 'general')
        )
        
        return jsonify(issue), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 400

# Actualizar ubicación del repartidor
@bp.route('/location', methods=['PUT'])
@jwt_required()
@delivery_required
def update_delivery_location():
    """Actualizar ubicación actual del repartidor"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if 'latitud' not in data or 'longitud' not in data:
        return jsonify({'message': 'Se requiere latitud y longitud'}), 400
    
    try:
        result = delivery_service.update_location(
            repartidor_id=user_id,
            latitud=data['latitud'],
            longitud=data['longitud']
        )
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 400

# Obtener repartidores disponibles (solo admin/empleado)
@bp.route('/drivers/available', methods=['GET'])
@jwt_required()
@admin_required
def get_available_drivers():
    """Obtener lista de repartidores disponibles"""
    drivers = delivery_service.get_available_drivers()
    
    from app.schemas.user import UserSchema
    user_schema = UserSchema(many=True, only=["id", "nombre", "apellido", "telefono"])
    return jsonify(user_schema.dump(drivers)), 200

# Obtener estadísticas de entregas para dashboard
@bp.route('/stats', methods=['GET'])
@jwt_required()
@delivery_required
def get_delivery_stats():
    """Obtener estadísticas de entregas para el panel de control"""
    user_id = get_jwt_identity()
    
    # Verificar rol del usuario
    from app.services.auth_service import AuthService
    auth_service = AuthService()
    user_role = auth_service.get_user_role(user_id)
    
    if user_role in ['administrador', 'empleado']:
        # Para admin/empleado, estadísticas generales
        repartidor_id = request.args.get('repartidor_id')
    else:
        # Para repartidor, solo sus estadísticas
        repartidor_id = user_id
    
    # Periodo de tiempo (hoy, esta semana, este mes)
    periodo = request.args.get('periodo', 'hoy')
    
    stats = delivery_service.get_delivery_stats(
        repartidor_id=repartidor_id,
        periodo=periodo
    )
    
    return jsonify(stats), 200