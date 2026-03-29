from app.models import db
from app.models.user import User, Role
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token
import uuid
from datetime import datetime, timedelta
import os

def login(email, password):
    """
    Autenticar un usuario y generar token JWT
    """
    user = User.get_by_email(email)
    
    if not user or not user.check_password(password):
        return None, "Credenciales inválidas"
    
    if not user.activo:
        return None, "Usuario inactivo"
    
    # Actualizar el último acceso
    user.ultimo_acceso = datetime.utcnow()
    db.session.commit()
    
    # Crear token JWT
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={
            'email': user.email,
            'rol_id': user.rol_id,
            'nombre': user.nombre
        }
    )
    
    return {
        'access_token': access_token,
        'user': user.to_dict()
    }, "Login exitoso"

def register_employee(data, admin_user):
    """
    Registrar un nuevo empleado (solo administradores pueden hacerlo)
    """
    # Verificar que el usuario que registra sea administrador
    if admin_user.rol_id != 1:  # 1 es el ID del rol administrador
        return None, "No tienes permisos para registrar empleados"
    
    # Verificar si el email ya existe
    if User.get_by_email(data['email']):
        return None, "El email ya está registrado"
    
    # Crear el nuevo usuario empleado
    new_user = User(
        email=data['email'],
        nombre=data['nombre'],
        apellido=data['apellido'],
        telefono=data['telefono'],
        rol_id=2,  # 2 es el ID del rol empleado
        activo=True,
        fecha_registro=datetime.utcnow()
    )
    
    # Establecer la contraseña
    new_user.set_password(data['password'])
    
    # Guardar en la base de datos
    db.session.add(new_user)
    db.session.commit()
    
    return new_user.to_dict(), "Empleado registrado exitosamente"

def register_customer(data):
    """
    Registrar un nuevo cliente
    """
    # Verificar si el email ya existe
    if User.get_by_email(data['email']):
        return None, "El email ya está registrado"
    
    # Crear el nuevo usuario cliente
    new_user = User(
        email=data['email'],
        password=data['password'],
        nombre=data['nombre'],
        apellido=data['apellido'],
        telefono=data['telefono'],
        rol_id=4  # 4 es el ID del rol cliente
    )
    
    # Establecer los valores adicionales después de crear el objeto
    new_user.activo = True
    new_user.fecha_registro = datetime.utcnow()
    
    # Guardar en la base de datos
    db.session.add(new_user)
    db.session.commit()
    
    # Crear token JWT
    access_token = create_access_token(
        identity=str(new_user.id),
        additional_claims={
            'email': new_user.email,
            'rol_id': new_user.rol_id,
            'nombre': new_user.nombre
        }
    )
    
    return {
        'access_token': access_token,
        'user': new_user.to_dict()
    }, "Cliente registrado exitosamente"

def create_default_admin():
    """
    Crea el usuario administrador por defecto si no existe
    """
    admin_email = os.getenv('ADMIN_EMAIL', 'admin@barrilfood.com')
    admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
    
    # Verificar si ya existe un administrador
    admin = User.get_by_email(admin_email)
    
    if not admin:
        # Verificar que exista el rol de administrador
        admin_role = Role.query.filter_by(id=1).first()
        if not admin_role:
            admin_role = Role(id=1, nombre='administrador', descripcion='Acceso completo al sistema')
            db.session.add(admin_role)
            db.session.commit()
        
        # Crear el administrador por defecto
        admin = User(
            email=admin_email,
            password=admin_password,
            nombre='Administrador',
            apellido='Sistema',
            telefono='1234567890',
            rol_id=1  # 1 es el ID del rol administrador
        )
        
        db.session.add(admin)
        db.session.commit()
        
        print(f"Usuario administrador creado con email: {admin_email}")
    
    return admin