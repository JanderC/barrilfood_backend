from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.services.report_service import ReportService
from app.utils.decorators import admin_required, employee_required
from datetime import datetime

# Crear el blueprint
bp = Blueprint('reports', __name__, url_prefix='/api/reports')
report_service = ReportService()

# Informe de ventas
@bp.route('/sales', methods=['GET'])
@jwt_required()
@employee_required
def get_sales_report():
    """Obtener informe de ventas en un periodo"""
    # Parámetros opcionales
    fecha_inicio = request.args.get('fecha_inicio', datetime.now().strftime('%Y-%m-01'))
    fecha_fin = request.args.get('fecha_fin', datetime.now().strftime('%Y-%m-%d'))
    agrupar_por = request.args.get('agrupar_por', 'dia')  # dia, semana, mes
    
    report = report_service.get_sales_report(
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        agrupar_por=agrupar_por
    )
    
    return jsonify(report), 200

# Informe de productos más vendidos
@bp.route('/top-products', methods=['GET'])
@jwt_required()
@employee_required
def get_top_products_report():
    """Obtener informe de productos más vendidos"""
    # Parámetros opcionales
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    limite = request.args.get('limite', 10, type=int)
    categoria_id = request.args.get('categoria_id', type=int)
    
    report = report_service.get_top_products(
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        limite=limite,
        categoria_id=categoria_id
    )
    
    return jsonify(report), 200

# Informe de tiempo de entrega promedio
@bp.route('/delivery-time', methods=['GET'])
@jwt_required()
@employee_required
def get_delivery_time_report():
    """Obtener informe de tiempos de entrega"""
    # Parámetros opcionales
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    agrupar_por = request.args.get('agrupar_por', 'dia')  # dia, semana, mes, repartidor
    
    report = report_service.get_delivery_time_report(
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        agrupar_por=agrupar_por
    )
    
    return jsonify(report), 200

# Informe de ventas por categoría
@bp.route('/sales-by-category', methods=['GET'])
@jwt_required()
@employee_required
def get_sales_by_category():
    """Obtener informe de ventas por categoría"""
    # Parámetros opcionales
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
    report = report_service.get_sales_by_category(
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin
    )
    
    return jsonify(report), 200

# Informe de rendimiento de repartidores
@bp.route('/delivery-performance', methods=['GET'])
@jwt_required()
@admin_required
def get_delivery_performance():
    """Obtener informe de rendimiento de repartidores"""
    # Parámetros opcionales
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    repartidor_id = request.args.get('repartidor_id')
    
    report = report_service.get_delivery_performance(
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        repartidor_id=repartidor_id
    )
    
    return jsonify(report), 200

# Informe de valoraciones y comentarios
@bp.route('/reviews', methods=['GET'])
@jwt_required()
@employee_required
def get_reviews_report():
    """Obtener informe de valoraciones y comentarios"""
    # Parámetros opcionales
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    producto_id = request.args.get('producto_id', type=int)
    calificacion_min = request.args.get('calificacion_min', type=int)
    calificacion_max = request.args.get('calificacion_max', type=int)
    
    report = report_service.get_reviews_report(
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        producto_id=producto_id,
        calificacion_min=calificacion_min,
        calificacion_max=calificacion_max
    )
    
    return jsonify(report), 200

# Dashboard con métricas generales
@bp.route('/dashboard', methods=['GET'])
@jwt_required()
@employee_required
def get_dashboard_data():
    """Obtener datos para el dashboard administrativo"""
    # Parámetros opcionales
    periodo = request.args.get('periodo', 'hoy')  # hoy, semana, mes, año
    
    data = report_service.get_dashboard_data(periodo=periodo)
    
    return jsonify(data), 200

# Exportar informe a Excel/CSV
@bp.route('/export/<string:report_type>', methods=['GET'])
@jwt_required()
@admin_required
def export_report(report_type):
    """Exportar un informe a formato Excel o CSV"""
    if report_type not in ['sales', 'products', 'categories', 'delivery', 'reviews']:
        return jsonify({'message': 'Tipo de informe no válido'}), 400
    
    # Parámetros opcionales
    formato = request.args.get('formato', 'excel')  # excel o csv
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
    try:
        # Esta función debería devolver el archivo para descarga
        # Para simplificar, retornamos un mensaje de éxito
        file_data = report_service.export_report(
            report_type=report_type,
            formato=formato,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
        
        # En una implementación real, aquí se devolvería el archivo
        # con send_file de Flask
        return jsonify({'message': f'Informe {report_type} exportado correctamente en formato {formato}'}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 400