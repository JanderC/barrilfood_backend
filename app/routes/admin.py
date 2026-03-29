from flask import Blueprint, request, jsonify
from app.services.admin_service import (
    get_all_employees, 
    get_employee_by_id, 
    create_employee, 
    update_employee, 
    toggle_employee_status, 
    delete_employee
)
from app.utils.validators import validate_register_data, validate_update_user_data
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User

bp = Blueprint('admin', __name__, url_prefix='/api/admin')

def check_admin_permissions():
    """
    Función auxiliar para verificar permisos de administrador
    """
    current_user_id = get_jwt_identity()
    current_user = User.query.filter_by(id=current_user_id).first()
    
    if not current_user:
        return None, "Usuario no encontrado"
    
    if current_user.rol_id != 1:  # 1 es el ID del rol administrador
        return None, "No tienes permisos de administrador"
    
    return current_user, None

@bp.route('/employees', methods=['GET'])
@jwt_required()
def get_employees():
    """
    Obtener todos los empleados
    """
    current_user, error = check_admin_permissions()
    if error:
        return jsonify({'error': error}), 403
        
    employees = get_all_employees()
    
    return jsonify({
        'message': 'Lista de empleados',
        'data': employees
    }), 200

@bp.route('/employees/<employee_id>', methods=['GET'])
@jwt_required()
def get_employee(employee_id):
    """
    Obtener un empleado por su ID
    """
    current_user, error = check_admin_permissions()
    if error:
        return jsonify({'error': error}), 403
        
    employee, message = get_employee_by_id(employee_id)
    
    if not employee:
        return jsonify({'error': message}), 404
    
    return jsonify({
        'message': message,
        'data': employee
    }), 200

@bp.route('/employees', methods=['POST'])
@jwt_required()
def create_employee_route():
    """
    Crear un nuevo empleado
    """
    current_user, error = check_admin_permissions()
    if error:
        return jsonify({'error': error}), 403
    
    data = request.get_json()
    
    # Validar datos de entrada
    validation_errors = validate_register_data(data)
    if validation_errors:
        return jsonify({'error': validation_errors}), 400
    
    # Verificar que se incluya el rol_id
    if 'rol_id' not in data:
        return jsonify({'error': 'El campo rol_id es requerido'}), 400
    
    # Procesar la creación del empleado
    result, message = create_employee(data, current_user)
    
    if not result:
        return jsonify({'error': message}), 400
    
    return jsonify({
        'message': message,
        'data': result
    }), 201

@bp.route('/employees/<employee_id>', methods=['PUT'])
@jwt_required()
def update_employee_route(employee_id):
    """
    Actualizar datos de un empleado
    """
    current_user, error = check_admin_permissions()
    if error:
        return jsonify({'error': error}), 403
    
    data = request.get_json()
    
    # Validar datos de entrada
    validation_errors = validate_update_user_data(data)
    if validation_errors:
        return jsonify({'error': validation_errors}), 400
    
    # Procesar la actualización
    result, message = update_employee(employee_id, data, current_user)
    
    if not result:
        return jsonify({'error': message}), 400
    
    return jsonify({
        'message': message,
        'data': result
    }), 200

@bp.route('/employees/<employee_id>/toggle-status', methods=['PUT'])
@jwt_required()
def toggle_employee_status_route(employee_id):
    """
    Activar/desactivar un empleado
    """
    current_user, error = check_admin_permissions()
    if error:
        return jsonify({'error': error}), 403
    
    result, message = toggle_employee_status(employee_id, current_user)
    
    if not result:
        return jsonify({'error': message}), 400
    
    return jsonify({
        'message': message,
        'data': result
    }), 200

@bp.route('/employees/<employee_id>', methods=['DELETE'])
@jwt_required()
def delete_employee_route(employee_id):
    """
    Eliminar un empleado
    """
    current_user, error = check_admin_permissions()
    if error:
        return jsonify({'error': error}), 403
    
    result, message = delete_employee(employee_id, current_user)
    
    if not result:
        return jsonify({'error': message}), 400
    
    return jsonify({
        'message': message,
        'data': result
    }), 200

@bp.route('/dashboard', methods=['GET'])
@jwt_required()
def admin_dashboard():
    """
    Obtener estadísticas para el dashboard de administrador
    """
    current_user, error = check_admin_permissions()
    if error:
        return jsonify({'error': error}), 403
    
    # Aquí se implementarían las estadísticas necesarias para el dashboard
    # como número de pedidos, ingresos, usuarios activos, etc.
    
    return jsonify({
        'message': 'Estadísticas del dashboard',
        'data': {
            # Aquí agregarías los datos del dashboard
            'total_empleados': len(get_all_employees()),
            # Añadir más estadísticas según necesidad
        }
    }), 200