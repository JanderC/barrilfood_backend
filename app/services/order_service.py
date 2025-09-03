from sqlalchemy import func
from app.models.order import OpcionSeleccionada, Pedido, MetodoPago, EstadoPedido   
from app.models.order import DetallePedido
from app.models.order import DetallePedido, OpcionSeleccionada, HistorialEstadoPedido
from app.models.product import Producto
from app.models.review import Valoracion
from app import db
from datetime import datetime   
import uuid

class OrderService:
    def get_orders(self, usuario_id=None, estado_id=None, fecha_inicio=None, fecha_fin=None, repartidor_id=None):
        """Obtener pedidos con filtros opcionales"""
        query = Pedido.query
        
        # Aplicar filtros si están presentes
        if usuario_id:
            query = query.filter(Pedido.usuario_id == usuario_id)
        
        if estado_id:
            query = query.filter(Pedido.estado_id == estado_id)
        
        if repartidor_id:
            query = query.filter(Pedido.repartidor_id == repartidor_id)
        
        if fecha_inicio:
            try:
                fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
                query = query.filter(Pedido.fecha_pedido >= fecha_inicio_dt)
            except ValueError:
                pass
        
        if fecha_fin:
            try:
                fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')
                # Añadir un día para incluir todo el día especificado
                fecha_fin_dt = fecha_fin_dt.replace(hour=23, minute=59, second=59)
                query = query.filter(Pedido.fecha_pedido <= fecha_fin_dt)
            except ValueError:
                pass
        
        # Ordenar por fecha, más recientes primero
        return query.order_by(Pedido.fecha_pedido.desc()).all()
    
    def get_order_by_id(self, order_id):
        """Obtener un pedido por su ID"""
        return Pedido.query.get(order_id)
    
    def create_order(self, order_data):
        """Crear un nuevo pedido"""
        try:
            # Crear pedido principal
            new_order = Pedido(
                usuario_id=order_data['usuario_id'],
                direccion_id=order_data['direccion_id'],
                estado_id=1,  # Estado inicial: pendiente
                metodo_pago_id=order_data['metodo_pago_id'],
                fecha_pedido=datetime.now(),
                subtotal=order_data['subtotal'],
                costo_envio=order_data.get('costo_envio', 0),
                descuento=order_data.get('descuento', 0),
                impuestos=order_data.get('impuestos', 0),
                total=order_data['total'],
                notas=order_data.get('notas', '')
            )
            
            db.session.add(new_order)
            db.session.flush()  # Para obtener el ID generado
            
            # Agregar detalles del pedido
            for item in order_data['items']:
                # Verificar disponibilidad del producto
                product = Producto.query.get(item['producto_id'])
                if not product or not product.disponible:
                    db.session.rollback()
                    raise Exception(f"El producto {item['producto_id']} no está disponible")
                
                # CAMBIO: Usar DetallePedido en lugar de DetallesPedido
                detail = DetallePedido(
                    pedido_id=new_order.id,
                    producto_id=item['producto_id'],
                    cantidad=item['cantidad'],
                    precio_unitario=item['precio_unitario'],
                    subtotal=item['subtotal'],
                    notas=item.get('notas', '')
                )
                db.session.add(detail)
                db.session.flush()  # IMPORTANTE: flush para obtener el ID del detalle
                
                # Agregar opciones seleccionadas si existen
                if 'opciones' in item and item['opciones']:
                    for opcion in item['opciones']:
                        # CAMBIO: Usar OpcionSeleccionada directamente (ya importado)
                        selected_option = OpcionSeleccionada(
                            detalle_pedido_id=detail.id,
                            opcion_id=opcion['opcion_id'],
                            precio=opcion['precio']
                        )
                        db.session.add(selected_option)
            
            # CAMBIO: Usar HistorialEstadoPedido en lugar de HistorialEstadosPedido
            history_entry = HistorialEstadoPedido(
                pedido_id=new_order.id,
                estado_id= 1,  # pendiente
                usuario_id=order_data['usuario_id'],
                notas="Pedido creado"
            )
            db.session.add(history_entry)
            
            # Confirmar transacción
            db.session.commit()
            return new_order
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    def update_order_status(self, order_id, estado_id, usuario_id, notas=None):
        """Actualizar el estado de un pedido"""
        order = self.get_order_by_id(order_id)
        if not order:
            raise Exception("Pedido no encontrado")
        
        # Verificar si el estado existe
        estado = EstadoPedido.query.get(estado_id)
        if not estado:
            raise Exception("Estado de pedido no válido")
        
        try:
            # Actualizar estado del pedido
            order.estado_id = estado_id
            
            # Si el estado es "entregado", actualizar fecha de entrega
            if estado_id == 6:  # entregado
                order.fecha_entrega_real = datetime.now()
            
            # Registrar cambio en el historial
            history_entry = HistorialEstadoPedido(
                pedido_id=order_id,
                estado_id=estado_id,
                usuario_id=usuario_id,
                notas=notas or f"Cambio de estado a {estado.nombre}"
            )
            db.session.add(history_entry)
            
            db.session.commit()
            return order
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    def assign_delivery(self, order_id, repartidor_id):
        """Asignar un repartidor a un pedido"""
        order = self.get_order_by_id(order_id)
        if not order:
            raise Exception("Pedido no encontrado")
        
        # Verificar que el usuario sea un repartidor
        from app.services.auth_service import AuthService
        auth_service = AuthService()
        user_role = auth_service.get_user_role(repartidor_id)
        
        if user_role != 'repartidor':
            raise Exception("El usuario asignado debe ser un repartidor")
        
        try:
            # Asignar repartidor
            order.repartidor_id = repartidor_id
            
            # Si el pedido está en estado "listo para entrega", cambiarlo a "en camino"
            if order.estado_id == 4:  # listo para entrega
                order.estado_id = 5  # en camino
                
                # Registrar cambio en el historial
                history_entry = HistorialEstadoPedido(
                    pedido_id=order_id,
                    estado_id=5,
                    usuario_id=repartidor_id,
                    notas="Pedido asignado a repartidor y en camino"
                )
                db.session.add(history_entry)
            
            db.session.commit()
            return order
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    def cancel_order(self, order_id, usuario_id, motivo=None):
        """Cancelar un pedido"""
        order = self.get_order_by_id(order_id)
        if not order:
            raise Exception("Pedido no encontrado")
        
        # Verificar que el pedido esté en un estado que permita cancelación
        if order.estado_id not in [1, 2]:  # pendiente o confirmado
            raise Exception("Este pedido ya no puede ser cancelado")
        
        try:
            # Actualizar estado a cancelado
            order.estado_id = 7  # cancelado
            
            # Registrar cambio en el historial
            history_entry = HistorialEstadoPedido(
                pedido_id=order_id,
                estado_id=7,
                usuario_id=usuario_id,
                notas=f"Pedido cancelado. Motivo: {motivo or 'No especificado'}"
            )
            db.session.add(history_entry)
            
            # Si se implementa gestión de inventario, devolver productos al stock
            # ...
            
            db.session.commit()
            return order
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    def get_order_history(self, order_id):
        """Obtener historial de estados de un pedido"""
        history = HistorialEstadoPedido.query.filter_by(pedido_id=order_id)\
            .order_by(HistorialEstadoPedido.fecha.desc())\
            .all()
        
        # Formatear resultados
        result = []
        for entry in history:
            estado = EstadoPedido.query.get(entry.estado_id)
            from app.models.user import Usuario
            usuario = Usuario.query.get(entry.usuario_id)
            
            result.append({
                'id': entry.id,
                'fecha': entry.fecha.isoformat(),
                'estado': {
                    'id': estado.id,
                    'nombre': estado.nombre,
                    'color': estado.color
                },
                'usuario': {
                    'id': usuario.id,
                    'nombre': f"{usuario.nombre} {usuario.apellido}"
                } if usuario else None,
                'notas': entry.notas
            })
        
        return result
    
    def add_review(self, pedido_id, usuario_id, producto_id, calificacion, comentario=None):
        """Añadir valoración a un producto de un pedido"""
        # Verificar que el pedido existe y está entregado
        order = self.get_order_by_id(pedido_id)
        if not order:
            raise Exception("Pedido no encontrado")
        
        if order.estado_id != 6:  # entregado
            raise Exception("Solo puedes valorar pedidos que hayan sido entregados")
        
        # Verificar que el producto pertenece al pedido
        product_in_order = False
        for detail in order.detalles:
            if detail.producto_id == producto_id:
                product_in_order = True
                break
        
        if not product_in_order:
            raise Exception("El producto no pertenece a este pedido")
        
        # Verificar que la calificación es válida
        if not 1 <= calificacion <= 5:
            raise Exception("La calificación debe estar entre 1 y 5")
        
        try:
            # Crear valoración
            review = Valoracion(
                pedido_id=pedido_id,
                usuario_id=usuario_id,
                producto_id=producto_id,
                calificacion=calificacion,
                comentario=comentario or ""
            )
            
            db.session.add(review)
            db.session.commit()
            
            return {
                'id': review.id,
                'pedido_id': review.pedido_id,
                'producto_id': review.producto_id,
                'calificacion': review.calificacion,
                'comentario': review.comentario,
                'fecha': review.fecha.isoformat()
            }
            
        except Exception as e:
            db.session.rollback()
            raise e