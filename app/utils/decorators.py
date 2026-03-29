# En app/utils/decorators.py (completo)
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.models.user import User

def admin_required(f):
    """
    Decorador para verificar que el usuario sea administrador
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()  # Asegura que hay un token válido
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        #user = User.get_by_id(current_user_id)
        
        if not user or user.rol_id != 1:  # 1 es el ID del rol administrador
            return jsonify({'error': 'Se requieren privilegios de administrador'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

def employee_required(f):
    """
    Decorador para verificar que el usuario sea empleado o administrador
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()  # Asegura que hay un token válido
        current_user_id = get_jwt_identity()
        user = User.get_by_id(current_user_id)
        
        if not user or (user.rol_id != 1 and user.rol_id != 2):  # 1=admin, 2=empleado
            return jsonify({'error': 'Se requieren privilegios de empleado o administrador'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

def delivery_required(f):
    """
    Decorador para verificar que el usuario sea repartidor o administrador
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()  # Asegura que hay un token válido
        current_user_id = get_jwt_identity()
        user = User.get_by_id(current_user_id)
        
        if not user or (user.rol_id != 1 and user.rol_id != 3):  # 1=admin, 3=repartidor
            return jsonify({'error': 'Se requieren privilegios de repartidor o administrador'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function