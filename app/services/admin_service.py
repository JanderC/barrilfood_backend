from app.models import db
from app.models.user import User, Role
from werkzeug.security import generate_password_hash
from datetime import datetime
import uuid

def get_all_employees():
    """
    Obtener todos los empleados (roles 2: empleado y 3: repartidor)
    """
    employees = User.query.filter(User.rol_id.in_([2, 3])).all()
    return [employee.to_dict() for employee in employees]

def get_employee_by_id(employee_id):
    """
    Obtener un empleado por su ID
    """
    try:
        employee = User.query.filter_by(id=uuid.UUID(employee_id)).first()
        if not employee or employee.rol_id not in [2, 3]:
            return None, "Empleado no encontrado"
        return employee.to_dict(), "Empleado encontrado"
    except ValueError:
        return None, "ID de empleado inválido"

def create_employee(data, admin_user):
    """
    Crear un nuevo empleado o repartidor
    """
    # Verificar que el usuario que crea sea administrador
    if admin_user.rol_id != 1:  # 1 es el ID del rol administrador
        return None, "No tienes permisos para crear empleados"
    
    # Verificar si el email ya existe
    if User.get_by_email(data['email']):
        return None, "El email ya está registrado"
    
    # Validar que el rol sea válido (2: empleado o 3: repartidor)
    if data['rol_id'] not in [2, 3]:
        return None, "Rol inválido. Debe ser empleado (2) o repartidor (3)"
    
    # Crear el nuevo usuario empleado
    new_user = User(
        email=data['email'],
        password=data['password'],
        nombre=data['nombre'],
        apellido=data['apellido'],
        telefono=data['telefono'],
        rol_id=data['rol_id']
    )
    
    # Establecer valores adicionales
    new_user.activo = True
    new_user.fecha_registro = datetime.utcnow()
    
    # Guardar en la base de datos
    db.session.add(new_user)
    db.session.commit()
    
    return new_user.to_dict(), "Empleado registrado exitosamente"

def update_employee(employee_id, data, admin_user):
    """
    Actualizar datos de un empleado
    """
    # Verificar que el usuario que actualiza sea administrador
    if admin_user.rol_id != 1:  # 1 es el ID del rol administrador
        return None, "No tienes permisos para actualizar empleados"
    
    try:
        # Buscar el empleado
        employee = User.query.filter_by(id=uuid.UUID(employee_id)).first()
        if not employee or employee.rol_id not in [2, 3]:
            return None, "Empleado no encontrado"
            
        # Verificar si se está cambiando el email y si ya existe
        if 'email' in data and data['email'] != employee.email:
            existing_user = User.get_by_email(data['email'])
            if existing_user:
                return None, "El email ya está registrado por otro usuario"
        
        # Actualizar campos
        for key, value in data.items():
            if key == 'password':
                employee.set_password(value)
            elif key == 'rol_id':
                if value not in [2, 3]:  # Solo permitir roles de empleado o repartidor
                    return None, "Rol inválido. Debe ser empleado (2) o repartidor (3)"
                setattr(employee, key, value)
            elif hasattr(employee, key):
                setattr(employee, key, value)
        
        # Guardar cambios
        db.session.commit()
        
        return employee.to_dict(), "Empleado actualizado exitosamente"
    except ValueError:
        return None, "ID de empleado inválido"

def toggle_employee_status(employee_id, admin_user):
    """
    Activar/desactivar un empleado
    """
    # Verificar que el usuario que actualiza sea administrador
    if admin_user.rol_id != 1:  # 1 es el ID del rol administrador
        return None, "No tienes permisos para modificar el estado de los empleados"
    
    try:
        # Buscar el empleado
        employee = User.query.filter_by(id=uuid.UUID(employee_id)).first()
        if not employee or employee.rol_id not in [2, 3]:
            return None, "Empleado no encontrado"
        
        # Cambiar el estado
        employee.activo = not employee.activo
        db.session.commit()
        
        status = "activado" if employee.activo else "desactivado"
        return employee.to_dict(), f"Empleado {status} exitosamente"
    except ValueError:
        return None, "ID de empleado inválido"

def delete_employee(employee_id, admin_user):
    """
    Eliminar un empleado
    """
    # Verificar que el usuario que elimina sea administrador
    if admin_user.rol_id != 1:  # 1 es el ID del rol administrador
        return None, "No tienes permisos para eliminar empleados"
    
    try:
        # Buscar el empleado
        employee = User.query.filter_by(id=uuid.UUID(employee_id)).first()
        if not employee or employee.rol_id not in [2, 3]:
            return None, "Empleado no encontrado"
        
        # Eliminar el empleado
        db.session.delete(employee)
        db.session.commit()
        
        return {"id": str(employee_id)}, "Empleado eliminado exitosamente"
    except ValueError:
        return None, "ID de empleado inválido"