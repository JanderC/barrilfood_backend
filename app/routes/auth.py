from flask import Blueprint, request, jsonify
from app.services.auth_service import login, register_employee, register_customer
from app.utils.validators import validate_login_data, validate_register_data
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/login', methods=['POST'])
def login_route():
    """
    Ruta para autenticar usuarios
    """
    data = request.get_json()
    
    # Validar datos de entrada
    validation_errors = validate_login_data(data)
    if validation_errors:
        return jsonify({'error': validation_errors}), 400
    
    # Procesar el login
    result, message = login(data['email'], data['password'])
    
    if not result:
        return jsonify({'error': message}), 401
    
    return jsonify({
        'message': message,
        'data': result
    }), 200

@bp.route('/register/employee', methods=['POST'])
@jwt_required()
def register_employee_route():
    """
    Ruta para registrar empleados (solo administradores)
    """
    # Obtener el ID del usuario autenticado
    current_user_id = get_jwt_identity()
    current_user = User.get_by_id(current_user_id)
    
    if not current_user:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    data = request.get_json()
    
    # Validar datos de entrada
    validation_errors = validate_register_data(data)
    if validation_errors:
        return jsonify({'error': validation_errors}), 400
    
    # Procesar el registro de empleado
    result, message = register_employee(data, current_user)
    
    if not result:
        return jsonify({'error': message}), 400
    
    return jsonify({
        'message': message,
        'data': result
    }), 201

@bp.route('/register/customer', methods=['POST'])
def register_customer_route():
    """
    Ruta para registro de clientes
    """
    data = request.get_json()
    
    # Validar datos de entrada
    validation_errors = validate_register_data(data)
    if validation_errors:
        return jsonify({'error': validation_errors}), 400
    
    # Procesar el registro de cliente
    result, message = register_customer(data)
    
    if not result:
        return jsonify({'error': message}), 400
    
    return jsonify({
        'message': message,
        'data': result
    }), 201

# Añadir esto a app/routes/auth.py
@bp.route('/check-token', methods=['GET'])
@jwt_required()
def check_token():
    """
    Verifica si el token JWT es válido
    """
    current_user_id = get_jwt_identity()
    user = User.get_by_id(current_user_id)
    
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    return jsonify({
        'message': 'Token válido',
        'data': {
            'user': user.to_dict()
        }
    }), 200