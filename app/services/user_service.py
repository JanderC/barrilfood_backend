# app/services/user_service.py
from sqlalchemy import func
from app.models.user import User
from app.models.order import Pedido  # Asumiendo que existe este modelo
from app.models.order_detail import DetallesPedido
from app.models.order_history import HistorialEstadosPedido
from app.models.product import Producto
from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class UserService:
    
    def get_user_orders(self, usuario_id, estado_id=None, fecha_inicio=None, fecha_fin=None):
        """Obtener pedidos del usuario con filtros opcionales"""
        query = Pedido.query.filter_by(usuario_id=usuario_id)
        
        # Aplicar filtros si están presentes
        if estado_id:
            query = query.filter(Pedido.estado_id == estado_id)
        
        if fecha_inicio:
            try:
                fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
                query = query.filter(Pedido.fecha_pedido >= fecha_inicio_dt)
            except ValueError:
                pass
        
        if fecha_fin:
            try:
                fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')
                fecha_fin_dt = fecha_fin_dt.replace(hour=23, minute=59, second=59)
                query = query.filter(Pedido.fecha_pedido <= fecha_fin_dt)
            except ValueError:
                pass
        
        # Ordenar por fecha, más recientes primero
        return query.order_by(Pedido.fecha_pedido.desc()).all()
    
    def get_order_by_id(self, order_id, usuario_id):
        """Obtener un pedido específico del usuario"""
        return Pedido.query.filter_by(id=order_id, usuario_id=usuario_id).first()
    
    def take_order(self, order_id, usuario_id):
        """El usuario toma/acepta su pedido (cambiar estado a confirmado)"""
        order = self.get_order_by_id(order_id, usuario_id)
        
        if not order:
            raise Exception("Pedido no encontrado")
        
        # Verificar que el pedido esté en estado pendiente
        if order.estado_id != 1:  # 1 = pendiente
            raise Exception("El pedido ya ha sido procesado")
        
        try:
            # Cambiar estado a confirmado
            order.estado_id = 2  # 2 = confirmado
            
            # Registrar cambio en el historial
            history_entry = HistorialEstadosPedido(
                pedido_id=order_id,
                estado_id=2,
                usuario_id=usuario_id,
                notas="Pedido tomado/confirmado por el cliente"
            )
            db.session.add(history_entry)
            
            db.session.commit()
            return order
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    def update_order_status_by_user(self, order_id, usuario_id, nuevo_estado_id, notas=None):
        """Permitir al usuario cambiar el estado de su pedido (solo ciertos estados)"""
        order = self.get_order_by_id(order_id, usuario_id)
        
        if not order:
            raise Exception("Pedido no encontrado")
        
        # Estados que el usuario puede cambiar
        allowed_transitions = {
            1: [2, 7],  # pendiente -> confirmado o cancelado
            2: [7],     # confirmado -> cancelado
        }
        
        current_state = order.estado_id
        if current_state not in allowed_transitions:
            raise Exception("No puedes cambiar el estado de este pedido")
        
        if nuevo_estado_id not in allowed_transitions[current_state]:
            raise Exception("Transición de estado no permitida")
        
        try:
            # Actualizar estado
            order.estado_id = nuevo_estado_id
            
            # Registrar cambio en el historial
            history_entry = HistorialEstadosPedido(
                pedido_id=order_id,
                estado_id=nuevo_estado_id,
                usuario_id=usuario_id,
                notas=notas or f"Estado cambiado por el cliente"
            )
            db.session.add(history_entry)
            
            db.session.commit()
            return order
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    def update_user_profile(self, usuario_id, profile_data):
        """Actualizar datos personales del usuario"""
        user = User.query.get(usuario_id)
        
        if not user:
            raise Exception("Usuario no encontrado")
        
        try:
            # Actualizar campos permitidos
            if 'nombre' in profile_data:
                user.nombre = profile_data['nombre']
            
            if 'apellido' in profile_data:
                user.apellido = profile_data['apellido']
            
            if 'telefono' in profile_data:
                user.telefono = profile_data['telefono']
            
            # Verificar si el email ya existe (si se está cambiando)
            if 'email' in profile_data and profile_data['email'] != user.email:
                existing_user = User.query.filter_by(email=profile_data['email']).first()
                if existing_user:
                    raise Exception("El email ya está en uso")
                user.email = profile_data['email']
            
            db.session.commit()
            return user
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    def change_password(self, usuario_id, current_password, new_password):
        """Cambiar contraseña del usuario"""
        user = User.query.get(usuario_id)
        
        if not user:
            raise Exception("Usuario no encontrado")
        
        # Verificar contraseña actual
        if not user.check_password(current_password):
            raise Exception("La contraseña actual es incorrecta")
        
        # Validar nueva contraseña
        if len(new_password) < 6:
            raise Exception("La nueva contraseña debe tener al menos 6 caracteres")
        
        try:
            # Actualizar contraseña
            user.set_password(new_password)
            db.session.commit()
            
            return True
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    def get_order_details_with_products(self, order_id, usuario_id):
        """Obtener detalles completos de un pedido con información de productos"""
        order = self.get_order_by_id(order_id, usuario_id)
        
        if not order:
            raise Exception("Pedido no encontrado")
        
        # Obtener detalles del pedido con productos
        details = db.session.query(DetallesPedido, Producto)\
            .join(Producto, DetallesPedido.producto_id == Producto.id)\
            .filter(DetallesPedido.pedido_id == order_id)\
            .all()
        
        # Formatear respuesta
        order_data = {
            'id': str(order.id),
            'fecha_pedido': order.fecha_pedido.isoformat(),
            'estado_id': order.estado_id,
            'subtotal': float(order.subtotal),
            'costo_envio': float(order.costo_envio or 0),
            'descuento': float(order.descuento or 0),
            'impuestos': float(order.impuestos or 0),
            'total': float(order.total),
            'notas': order.notas,
            'items': []
        }
        
        for detail, product in details:
            order_data['items'].append({
                'id': detail.id,
                'producto_id': product.id,
                'producto_nombre': product.nombre,
                'producto_descripcion': product.descripcion,
                'cantidad': detail.cantidad,
                'precio_unitario': float(detail.precio_unitario),
                'subtotal': float(detail.subtotal),
                'notas': detail.notas
            })
        
        return order_data
    
    def get_order_history(self, order_id, usuario_id):
        """Obtener historial de estados de un pedido del usuario"""
        # Verificar que el pedido pertenece al usuario
        order = self.get_order_by_id(order_id, usuario_id)
        if not order:
            raise Exception("Pedido no encontrado")
        
        history = HistorialEstadosPedido.query.filter_by(pedido_id=order_id)\
            .order_by(HistorialEstadosPedido.fecha.desc())\
            .all()
        
        # Formatear resultados
        result = []
        for entry in history:
            # Obtener información del usuario que hizo el cambio
            usuario = User.query.get(entry.usuario_id)
            
            result.append({
                'id': entry.id,
                'fecha': entry.fecha.isoformat(),
                'estado_id': entry.estado_id,
                'usuario': {
                    'id': str(usuario.id),
                    'nombre': f"{usuario.nombre} {usuario.apellido}"
                } if usuario else None,
                'notas': entry.notas
            })
        
        return result