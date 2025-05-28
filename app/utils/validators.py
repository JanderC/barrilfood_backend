import re

def validate_email(email):
    """
    Validar formato de email
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password(password):
    """
    Validar que la contraseña tenga al menos 6 caracteres
    """
    return len(password) >= 6

def validate_phone(phone):
    """
    Validar formato de teléfono (básico)
    """
    pattern = r'^[0-9+\s()-]{7,20}$'
    return bool(re.match(pattern, phone))

def validate_login_data(data):
    """
    Validar datos de login
    """
    errors = []
    
    if not data.get('email'):
        errors.append("El email es requerido")
    elif not validate_email(data.get('email')):
        errors.append("El formato del email es inválido")
    
    if not data.get('password'):
        errors.append("La contraseña es requerida")
    
    return errors if errors else None

def validate_register_data(data):
    """
    Validar datos de registro
    """
    errors = []
    
    if not data.get('email'):
        errors.append("El email es requerido")
    elif not validate_email(data.get('email')):
        errors.append("El formato del email es inválido")
    
    if not data.get('password'):
        errors.append("La contraseña es requerida")
    elif not validate_password(data.get('password')):
        errors.append("La contraseña debe tener al menos 6 caracteres")
    
    if not data.get('nombre'):
        errors.append("El nombre es requerido")
    
    if not data.get('apellido'):
        errors.append("El apellido es requerido")
    
    if not data.get('telefono'):
        errors.append("El teléfono es requerido")
    elif not validate_phone(data.get('telefono')):
        errors.append("El formato del teléfono es inválido")
    
    return errors if errors else None
def is_valid_email(email):
    """
    Validar formato de email usando expresión regular
    """
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

def validate_update_user_data(data):
    """
    Validar datos de actualización de usuario
    """
    errors = {}
    
    # Verificar los campos opcionales si están presentes
    if 'email' in data and data['email']:
        if not is_valid_email(data['email']):
            errors['email'] = 'Email inválido'
    
    if 'password' in data and data['password']:
        if len(data['password']) < 6:
            errors['password'] = 'La contraseña debe tener al menos 6 caracteres'
    
    if 'telefono' in data and data['telefono']:
        if not is_valid_phone(data['telefono']):
            errors['telefono'] = 'Teléfono inválido. Debe contener solo números y tener entre 7 y 15 dígitos'
    
    if 'rol_id' in data:
        if data['rol_id'] not in [1, 2, 3, 4]:  # Validar que sea un rol válido
            errors['rol_id'] = 'Rol inválido'
    
    return errors if errors else None

def is_valid_phone(phone):
    """
    Validar formato de teléfono (números, entre 7 y 15 dígitos)
    """
    phone_regex = r'^\d{7,15}$'
    return re.match(phone_regex, phone) is not None

def validate_address_data(data):
    """
    Validar datos de dirección
    """
    errors = []
    
    if not data.get('direccion'):
        errors.append("La dirección es requerida")
    
    if not data.get('ciudad'):
        errors.append("La ciudad es requerida")
    
    # Validar coordenadas si están presentes
    if data.get('latitud') is not None:
        try:
            lat = float(data.get('latitud'))
            if lat < -90 or lat > 90:
                errors.append("La latitud debe estar entre -90 y 90")
        except ValueError:
            errors.append("La latitud debe ser un número válido")
    
    if data.get('longitud') is not None:
        try:
            lng = float(data.get('longitud'))
            if lng < -180 or lng > 180:
                errors.append("La longitud debe estar entre -180 y 180")
        except ValueError:
            errors.append("La longitud debe ser un número válido")
    
    return errors if errors else None