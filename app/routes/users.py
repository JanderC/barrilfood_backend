from flask import Blueprint, request, jsonify
from app.models.user import User
from app.models.address import Direccion
from app import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.validators import validate_address_data
from app.utils.decorators import admin_required

bp = Blueprint('users', __name__, url_prefix='/api/users')

@bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """
    Obtener el perfil del usuario autenticado
    """
    current_user_id = get_jwt_identity()
    user = User.get_by_id(current_user_id)
    
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    return jsonify({
        'data': user.to_dict()
    }), 200

@bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """
    Actualizar el perfil del usuario autenticado
    """
    current_user_id = get_jwt_identity()
    user = User.get_by_id(current_user_id)
    
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    data = request.get_json()
    
    # Actualizar campos permitidos
    if 'nombre' in data:
        user.nombre = data['nombre']
    
    if 'apellido' in data:
        user.apellido = data['apellido']
    
    if 'telefono' in data:
        user.telefono = data['telefono']
    
    # Si el usuario es administrador, puede cambiar el rol o estado de activación
    if user.rol_id == 1 and 'activo' in data:
        user.activo = data['activo']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Perfil actualizado exitosamente',
        'data': user.to_dict()
    }), 200

@bp.route('/address', methods=['POST'])
@jwt_required()
def add_address():
    """
    Agregar una dirección al usuario autenticado
    """
    current_user_id = get_jwt_identity()
    user = User.get_by_id(current_user_id)
    
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    data = request.get_json()
    
    # Validar datos de entrada
    validation_errors = validate_address_data(data)
    if validation_errors:
        return jsonify({'error': validation_errors}), 400
    
    # Si es la primera dirección o se marca como principal, actualizar las demás
    if data.get('es_principal', False) or not user.direcciones:
        # Obtener todas las direcciones del usuario y marcarlas como no principales
        for direccion in user.direcciones:
            direccion.es_principal = False
    
    # Crear la nueva dirección
    new_address = Direccion(
        usuario_id=user.id,
        direccion=data['direccion'],
        ciudad=data['ciudad'],
        barrio=data.get('barrio'),
        referencia=data.get('referencia'),
        latitud=data.get('latitud'),
        longitud=data.get('longitud'),
        es_principal=data.get('es_principal', False) or not user.direcciones
    )
    
    db.session.add(new_address)
    db.session.commit()
    
    return jsonify({
        'message': 'Dirección agregada exitosamente',
        'data': new_address.to_dict()
    }), 201

@bp.route('/address/<int:address_id>', methods=['PUT'])
@jwt_required()
def update_address(address_id):
    """
    Actualizar una dirección existente
    """
    current_user_id = get_jwt_identity()
    user = User.get_by_id(current_user_id)
    
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    # Buscar la dirección
    address = Direccion.query.filter_by(id=address_id, usuario_id=user.id).first()
    
    if not address:
        return jsonify({'error': 'Dirección no encontrada o no pertenece al usuario'}), 404
    
    data = request.get_json()
    
    # Validar datos de entrada
    validation_errors = validate_address_data(data)
    if validation_errors:
        return jsonify({'error': validation_errors}), 400
    
    # Si se está marcando como principal, actualizar las demás
    if data.get('es_principal', False) and not address.es_principal:
        # Obtener todas las direcciones del usuario y marcarlas como no principales
        for dir in user.direcciones:
            dir.es_principal = False
    
    # Actualizar los campos de la dirección
    address.direccion = data.get('direccion', address.direccion)
    address.ciudad = data.get('ciudad', address.ciudad)
    address.barrio = data.get('barrio', address.barrio)
    address.referencia = data.get('referencia', address.referencia)
    address.latitud = data.get('latitud', address.latitud)
    address.longitud = data.get('longitud', address.longitud)
    address.es_principal = data.get('es_principal', address.es_principal)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Dirección actualizada exitosamente',
        'data': address.to_dict()
    }), 200

@bp.route('/address/<int:address_id>', methods=['DELETE'])
@jwt_required()
def delete_address(address_id):
    """
    Eliminar una dirección
    """
    current_user_id = get_jwt_identity()
    user = User.get_by_id(current_user_id)
    
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    # Buscar la dirección
    address = Direccion.query.filter_by(id=address_id, usuario_id=user.id).first()
    
    if not address:
        return jsonify({'error': 'Dirección no encontrada o no pertenece al usuario'}), 404
    
    # Si la dirección es principal y hay otras direcciones, hacer otra principal
    if address.es_principal and len(user.direcciones) > 1:
        # Encontrar otra dirección para hacerla principal
        for dir in user.direcciones:
            if dir.id != address_id:
                dir.es_principal = True
                break
    
    db.session.delete(address)
    db.session.commit()
    
    return jsonify({
        'message': 'Dirección eliminada exitosamente'
    }), 200

@bp.route('/address', methods=['GET'])
@jwt_required()
def get_addresses():
    """
    Obtener todas las direcciones del usuario autenticado
    """
    current_user_id = get_jwt_identity()
    user = User.get_by_id(current_user_id)
    
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    addresses = [address.to_dict() for address in user.direcciones]
    
    return jsonify({
        'data': addresses
    }), 200

@bp.route('/', methods=['GET'])
@jwt_required()
@admin_required
def get_users():
    """
    Obtener lista de usuarios (solo para administradores)
    """
    users = User.query.all()
    users_list = [user.to_dict() for user in users]
    
    return jsonify({
        'data': users_list
    }), 200