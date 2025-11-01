# services/todo_service.py
from ..models import db, Tarea, Usuario
from datetime import datetime, date

class TodoService:
    
    @classmethod
    def obtener_listas_usuario(cls, usuario_id):
        """Obtiene todas las listas de tareas organizadas del usuario"""
        
        # Agrupar tareas por sala (lista)
        tareas = Tarea.query.filter_by(usuario_id=usuario_id).all()
        
        # Organizar por listas (salas) y tareas individuales
        listas = {}
        tareas_individuales = []
        
        for tarea in tareas:
            if tarea.sala_id:
                if tarea.sala_id not in listas:
                    from backend.models import Sala
                    sala = Sala.query.get(tarea.sala_id)
                    listas[tarea.sala_id] = {
                        'id': tarea.sala_id,
                        'nombre': sala.nombre if sala else 'Lista sin nombre',
                        'descripcion': sala.descripcion if sala else None,
                        'tareas': []
                    }
                listas[tarea.sala_id]['tareas'].append(tarea.to_dict())
            else:
                tareas_individuales.append(tarea.to_dict())
        
        return {
            'listas': list(listas.values()),
            'tareas_individuales': tareas_individuales
        }
    
    @classmethod
    def crear_lista(cls, usuario_id, nombre, descripcion=None, fecha_limite=None):
        """Crea una nueva lista de tareas (sala privada)"""
        
        if not nombre:
            raise ValueError("El nombre de la lista es requerido")
        
        from backend.models import Sala, UsuarioSala
        import secrets
        import string
        
        # Crear sala privada para la lista
        codigo_acceso = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        
        nueva_sala = Sala(
            nombre=nombre,
            descripcion=descripcion,
            max_participantes=1,
            es_privada=True,
            codigo_acceso=codigo_acceso
        )
        
        db.session.add(nueva_sala)
        db.session.flush()
        
        # Agregar al usuario como líder de la sala
        usuario_sala = UsuarioSala(
            usuario_id=usuario_id,
            sala_id=nueva_sala.sala_id,
            rol_en_sala='lider'
        )
        
        db.session.add(usuario_sala)
        db.session.commit()
        
        return {
            'id': nueva_sala.sala_id,
            'nombre': nueva_sala.nombre,
            'descripcion': nueva_sala.descripcion,
            'fecha_creacion': datetime.utcnow().isoformat(),
            'tareas': []
        }
    
    @classmethod
    def completar_tarea_anticipadamente(cls, usuario_id, tarea_id):
        """Marca una tarea como completada verificando si fue antes de tiempo"""
        
        tarea = Tarea.query.filter_by(tarea_id=tarea_id, usuario_id=usuario_id).first()
        
        if not tarea:
            raise ValueError("Tarea no encontrada")
        
        if tarea.estado == 'Completado':
            raise ValueError("La tarea ya está completada")
        
        hoy = date.today()
        completada_anticipadamente = False
        
        # Verificar si se completó antes de la fecha de vencimiento
        if tarea.fecha_vencimiento and hoy < tarea.fecha_vencimiento:
            completada_anticipadamente = True
            dias_anticipados = (tarea.fecha_vencimiento - hoy).days
        else:
            dias_anticipados = 0
        
        # Actualizar tarea
        tarea.estado = 'Completado'
        
        # Agregar comentario si se completó anticipadamente
        if completada_anticipadamente:
            comentario_anticipado = f"Completada {dias_anticipados} días antes de tiempo"
            if tarea.comentario:
                tarea.comentario += f" | {comentario_anticipado}"
            else:
                tarea.comentario = comentario_anticipado
        
        db.session.commit()
        
        return {
            'message': 'Tarea completada exitosamente',
            'tarea_id': tarea_id,
            'completada_anticipadamente': completada_anticipadamente,
            'dias_anticipados': dias_anticipados,
            'fecha_completada': hoy.isoformat(),
            'fecha_vencimiento': tarea.fecha_vencimiento.isoformat() if tarea.fecha_vencimiento else None
        }
    
    @classmethod
    def obtener_estadisticas_productividad(cls, usuario_id):
        """Obtiene estadísticas detalladas de productividad"""
        
        hoy = date.today()
        
        # Estadísticas básicas
        total_tareas = Tarea.query.filter_by(usuario_id=usuario_id).count()
        tareas_completadas = Tarea.query.filter_by(usuario_id=usuario_id, estado='Completado').count()
        
        # Tareas completadas anticipadamente
        tareas_anticipadas = Tarea.query.filter(
            Tarea.usuario_id == usuario_id,
            Tarea.estado == 'Completado',
            Tarea.comentario.like('%días antes de tiempo%')
        ).count()
        
        # Tareas vencidas
        tareas_vencidas = Tarea.query.filter(
            Tarea.usuario_id == usuario_id,
            Tarea.estado != 'Completado',
            Tarea.fecha_vencimiento < hoy
        ).count()
        
        # Tareas de esta semana
        inicio_semana = hoy - timedelta(days=hoy.weekday())
        fin_semana = inicio_semana + timedelta(days=6)
        
        tareas_semana = Tarea.query.filter(
            Tarea.usuario_id == usuario_id,
            Tarea.fecha_creacion >= inicio_semana,
            Tarea.fecha_creacion <= fin_semana
        ).count()
        
        tareas_completadas_semana = Tarea.query.filter(
            Tarea.usuario_id == usuario_id,
            Tarea.estado == 'Completado',
            Tarea.fecha_creacion >= inicio_semana,
            Tarea.fecha_creacion <= fin_semana
        ).count()
        
        return {
            'resumen_general': {
                'total_tareas': total_tareas,
                'completadas': tareas_completadas,
                'pendientes': total_tareas - tareas_completadas,
                'porcentaje_completadas': round((tareas_completadas / total_tareas) * 100, 2) if total_tareas > 0 else 0
            },
            'rendimiento': {
                'tareas_anticipadas': tareas_anticipadas,
                'tareas_vencidas': tareas_vencidas,
                'porcentaje_anticipadas': round((tareas_anticipadas / tareas_completadas) * 100, 2) if tareas_completadas > 0 else 0
            },
            'estadisticas_semanales': {
                'tareas_creadas': tareas_semana,
                'tareas_completadas': tareas_completadas_semana,
                'productividad_semanal': round((tareas_completadas_semana / tareas_semana) * 100, 2) if tareas_semana > 0 else 0
            }
        }