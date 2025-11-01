# services/pomodoro_service.py
from ..models import db, Sesion, Tecnica, SesionTecnicaParam
from datetime import datetime, timedelta
import uuid

class PomodoroService:
    TECNICA_POMODORO_ID = 'pomodoro'  # Asegúrate de que esta técnica exista en tu DB
    
    @classmethod
    def iniciar_pomodoro(cls, usuario_id, duracion_trabajo=25, duracion_descanso=5, ciclos_objetivo=4, modo_no_distraccion=False):
        """Inicia una nueva sesión de Pomodoro"""
        
        # Verificar que no hay otra sesión activa
        sesion_activa = Sesion.query.filter_by(
            usuario_id=usuario_id,
            estado='EnEjecucion'
        ).first()
        
        if sesion_activa:
            raise ValueError("Ya tienes una sesión en ejecución")
        
        # Obtener o crear técnica Pomodoro
        tecnica_pomodoro = Tecnica.query.filter_by(nombre='Pomodoro').first()
        if not tecnica_pomodoro:
            tecnica_pomodoro = Tecnica(
                nombre='Pomodoro',
                categoria='productividad'
            )
            db.session.add(tecnica_pomodoro)
            db.session.flush()
        
        # Crear sesión
        nueva_sesion = Sesion(
            usuario_id=usuario_id,
            tecnica_id=tecnica_pomodoro.tecnica_id,
            inicio=datetime.utcnow(),
            es_grupal=False,
            estado='EnEjecucion'
        )
        
        db.session.add(nueva_sesion)
        db.session.flush()
        
        # Agregar parámetros específicos del Pomodoro
        parametros = [
            {'codigo': 'duracion_trabajo', 'cantidad': str(duracion_trabajo)},
            {'codigo': 'duracion_descanso', 'cantidad': str(duracion_descanso)},
            {'codigo': 'ciclos_objetivo', 'cantidad': str(ciclos_objetivo)},
            {'codigo': 'ciclos_completados', 'cantidad': '0'},
            {'codigo': 'fase_actual', 'cantidad': 'trabajo'},
            {'codigo': 'tiempo_inicio_fase', 'cantidad': datetime.utcnow().isoformat()},
            {'codigo': 'modo_no_distraccion', 'cantidad': str(modo_no_distraccion)}
        ]
        
        for param in parametros:
            sesion_param = SesionTecnicaParam(
                sesion_id=nueva_sesion.sesion_id,
                codigo=param['codigo'],
                cantidad=param['cantidad']
            )
            db.session.add(sesion_param)
        
        db.session.commit()
        
        return cls._formatear_respuesta_pomodoro(nueva_sesion)
    
    @classmethod
    def completar_ciclo(cls, usuario_id, sesion_id, tipo_ciclo):
        """Completa un ciclo de trabajo o descanso"""
        
        sesion = Sesion.query.filter_by(
            sesion_id=sesion_id,
            usuario_id=usuario_id,
            estado='EnEjecucion'
        ).first()
        
        if not sesion:
            raise ValueError("Sesión no encontrada o no está en ejecución")
        
        # Obtener parámetros actuales
        parametros = {p.codigo: p.cantidad for p in sesion.parametros}
        
        ahora = datetime.utcnow()
        tiempo_inicio_fase = datetime.fromisoformat(parametros['tiempo_inicio_fase'])
        tiempo_transcurrido = (ahora - tiempo_inicio_fase).total_seconds() / 60  # minutos
        
        resultado = {
            'ciclo_completado': False,
            'fase_siguiente': None,
            'tiempo_transcurrido': tiempo_transcurrido,
            'ciclos_completados': int(parametros.get('ciclos_completados', 0))
        }
        
        if tipo_ciclo == 'trabajo':
            # Completar fase de trabajo
            ciclos_completados = int(parametros['ciclos_completados']) + 1
            
            # Actualizar ciclos completados
            param_ciclos = next((p for p in sesion.parametros if p.codigo == 'ciclos_completados'), None)
            if param_ciclos:
                param_ciclos.cantidad = str(ciclos_completados)
            
            # Cambiar a fase de descanso
            param_fase = next((p for p in sesion.parametros if p.codigo == 'fase_actual'), None)
            if param_fase:
                param_fase.cantidad = 'descanso'
            
            # Actualizar tiempo de inicio de fase
            param_tiempo = next((p for p in sesion.parametros if p.codigo == 'tiempo_inicio_fase'), None)
            if param_tiempo:
                param_tiempo.cantidad = ahora.isoformat()
            
            resultado.update({
                'ciclo_completado': True,
                'fase_siguiente': 'descanso',
                'ciclos_completados': ciclos_completados
            })
            
        elif tipo_ciclo == 'descanso':
            # Completar fase de descanso, volver a trabajo
            param_fase = next((p for p in sesion.parametros if p.codigo == 'fase_actual'), None)
            if param_fase:
                param_fase.cantidad = 'trabajo'
            
            # Actualizar tiempo de inicio de fase
            param_tiempo = next((p for p in sesion.parametros if p.codigo == 'tiempo_inicio_fase'), None)
            if param_tiempo:
                param_tiempo.cantidad = ahora.isoformat()
            
            resultado.update({
                'fase_siguiente': 'trabajo'
            })
        
        db.session.commit()
        return resultado
    
    @classmethod
    def finalizar_pomodoro(cls, usuario_id, sesion_id, completado_totalmente=False):
        """Finaliza una sesión de Pomodoro"""
        
        sesion = Sesion.query.filter_by(
            sesion_id=sesion_id,
            usuario_id=usuario_id,
            estado='EnEjecucion'
        ).first()
        
        if not sesion:
            raise ValueError("Sesión no encontrada o no está en ejecución")
        
        ahora = datetime.utcnow()
        duracion_total = int((ahora - sesion.inicio).total_seconds() / 60)
        
        # Actualizar sesión
        sesion.fin = ahora
        sesion.duracion_real = duracion_total
        sesion.estado = 'Completado' if completado_totalmente else 'Cancelado'
        
        db.session.commit()
        
        # Obtener estadísticas finales
        parametros = {p.codigo: p.cantidad for p in sesion.parametros}
        ciclos_completados = int(parametros.get('ciclos_completados', 0))
        ciclos_objetivo = int(parametros.get('ciclos_objetivo', 4))
        modo_no_distraccion = parametros.get('modo_no_distraccion', 'False') == 'True'
        
        return {
            'message': 'Pomodoro finalizado exitosamente',
            'sesion_id': sesion_id,
            'completado_totalmente': completado_totalmente,
            'ciclos_completados': ciclos_completados,
            'ciclos_objetivo': ciclos_objetivo,
            'duracion_total_minutos': duracion_total,
            'modo_no_distraccion': modo_no_distraccion,
            'porcentaje_completado': round((ciclos_completados / ciclos_objetivo) * 100, 2)
        }
    
    @classmethod
    def obtener_estado_pomodoro(cls, usuario_id, sesion_id):
        """Obtiene el estado actual de un Pomodoro en ejecución"""
        
        sesion = Sesion.query.filter_by(
            sesion_id=sesion_id,
            usuario_id=usuario_id
        ).first()
        
        if not sesion:
            raise ValueError("Sesión no encontrada")
        
        return cls._formatear_respuesta_pomodoro(sesion)
    
    @classmethod
    def _formatear_respuesta_pomodoro(cls, sesion):
        """Formatea la respuesta con información del Pomodoro"""
        parametros = {p.codigo: p.cantidad for p in sesion.parametros}
        
        ahora = datetime.utcnow()
        tiempo_transcurrido = 0
        if parametros.get('tiempo_inicio_fase'):
            tiempo_inicio_fase = datetime.fromisoformat(parametros['tiempo_inicio_fase'])
            tiempo_transcurrido = (ahora - tiempo_inicio_fase).total_seconds() / 60
        
        return {
            'sesion_id': sesion.sesion_id,
            'estado': sesion.estado,
            'inicio': sesion.inicio.isoformat(),
            'duracion_trabajo': int(parametros.get('duracion_trabajo', 25)),
            'duracion_descanso': int(parametros.get('duracion_descanso', 5)),
            'ciclos_objetivo': int(parametros.get('ciclos_objetivo', 4)),
            'ciclos_completados': int(parametros.get('ciclos_completados', 0)),
            'fase_actual': parametros.get('fase_actual', 'trabajo'),
            'tiempo_transcurrido_fase': round(tiempo_transcurrido, 2),
            'modo_no_distraccion': parametros.get('modo_no_distraccion', 'False') == 'True'
        }