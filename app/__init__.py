from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
from sqlalchemy import text  # Importar text de SQLAlchemy

# Importar la instancia db de models
from app.models import db, init_app

# Cargar variables de entorno
load_dotenv()

# Inicializar la aplicación Flask
app = Flask(__name__)

# Configuración
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'clave-secreta-por-defecto')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:p4ng34t3ch@200.40.68.122/barrilfood')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False    
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-clave')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 86400  # 24 horas

# Inicializar extensiones
init_app(app)  # Inicializar SQLAlchemy con la aplicación
migrate = Migrate(app, db)
jwt = JWTManager(app)
CORS(app)

# Configurar manejadores de errores JWT
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({
        'error': 'El token ha expirado',
        'code': 'token_expired'
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'error': 'Token inválido',
        'code': 'invalid_token'
    }), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        'error': 'No se proporcionó token de acceso',
        'code': 'authorization_required'
    }), 401


# Importar rutas después de crear la aplicación para evitar importaciones circulares
from app.routes import admin, auth, users, products, categories, orders, inventory, user_orders

# Registrar blueprints
app.register_blueprint(auth.bp)
app.register_blueprint(users.bp)
app.register_blueprint(products.bp)
app.register_blueprint(inventory.bp)
app.register_blueprint(categories.bp)
app.register_blueprint(orders.bp)
app.register_blueprint(admin.bp)
app.register_blueprint(user_orders.bp)

# Crear función para inicializar el usuario administrador por defecto
from app.services.auth_service import create_default_admin

# En versiones recientes de Flask, before_first_request está deprecado
# Se recomienda usar el evento before_first_request con app.before_request
_init_app = False

@app.before_request
def initialize_app():
    global _init_app
    if not _init_app:
        with app.app_context():
            create_default_admin()
        _init_app = True

# Función para verificar la conexión a la base de datos
def check_database_connection():
    try:
        # Intentar una consulta simple para verificar la conexión usando `text`
        with app.app_context():
            db.session.execute(text('SELECT 1'))  # Usar text() para la consulta SQL cruda
        print("Conexión a la base de datos exitosa.")
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")

# Verificar la conexión antes de iniciar el servidor
check_database_connection()

@app.route('/')
def hello():
    return "API de barrilfood funcionando correctamente con PostgreSQL y JWT!"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port)