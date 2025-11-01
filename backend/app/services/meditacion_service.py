# services/meditacion_service.py
from ..models import db, Sesion, Tecnica, SesionTecnicaParam
from datetime import datetime

class MeditacionService:
    
    TIPOS_MEDITACION = [
        {'id': 'mindfulness', 'nombre': 'Mindfulness', 'descripcion': 'Meditación de atención plena'},
        {'id': 'respiracion', 'nombre': 'Respiración', 'descripcion': 'Enfoque en la respiración'},
        {'id': 'body_scan', 'nombre': 'Body Scan', 'descripcion': 'Exploración corporal'},
        {'id': 'loving_kindness', 'nombre': 'Amor y Bondad', 'descripcion': 'Cultivo de compasión'},
        {'id': 'concentracion', 'nombre': 'Concentración', 'descripcion': 'Enfoque en un objeto específico'}
    ]
    
    @classmethod
    def iniciar_meditacion(cls, usuario_id, duracion, tipo_meditacion='mindfulness'):
        """Inicia una nueva sesión de meditación"""
        
        # Verificar que no hay otra sesión activa
        sesion_activa = Sesion.query.filter_by(
            usuario_id=usuario_id,
            estado='EnEjecucion'
        ).first()
        
        if sesion_activa:
            raise ValueError("Ya tienes una sesión en ejecución")
        
        # Validar tipo de meditación
        if not any(tipo['id'] == tipo_meditacion for tipo in cls.TIPOS_MEDITACION):
            raise ValueError("Tipo de meditación no válido")
        
        # Obtener o crear técnica Meditación
        tecnica_meditacion = Tecnica.query.filter_by(nombre='Meditación').first()
        if not tecnica_meditacion:
            tecnica_meditacion = Tecnica(
                nombre='Meditación',
                categoria='bienestar'
            )
            db.session.add(tecnica_meditacion)
            db.session.flush()
        
        # Crear sesión
        nueva_sesion = Sesion(
            usuario_id=usuario_id,
            tecnica_id=tecnica_meditacion.tecnica_id,
            inicio=datetime.utcnow(),
            es_grupal=False,
            estado='EnEjecucion'
        )
        
        db.session.add(nueva_sesion)
        db.session.flush()
        
        # Agregar parámetros específicos de la meditación
        parametros = [
            {'codigo': 'duracion_planificada', 'cantidad': str(duracion)},
            {'codigo': 'tipo_meditacion', 'cantidad': tipo_meditacion},
            {'codigo': 'tiempo_inicio', 'cantidad': datetime.utcnow().isoformat()}
        ]
        
        for param in parametros:
            sesion_param = SesionTecnicaParam(
                sesion_id=nueva_sesion.sesion_id,
                codigo=param['codigo'],
                cantidad=param['cantidad']
            )
            db.session.add(sesion_param)
        
        db.session.commit()
        
        return cls._formatear_respuesta_meditacion(nueva_sesion)
    
    @classmethod
    def finalizar_meditacion(cls, usuario_id, sesion_id, completada=True, calificacion=None):
        """Finaliza una sesión de meditación"""
        
        sesion = Sesion.query.filter_by(
            sesion_id=sesion_id,
            usuario_id=usuario_id,
            estado='EnEjecucion'
        ).first()
        
        if not sesion:
            raise ValueError("Sesión no encontrada o no está en ejecución")
        
        ahora = datetime.utcnow()
        duracion_real = int((ahora - sesion.inicio).total_seconds() / 60)
        
        # Actualizar sesión
        sesion.fin = ahora
        sesion.duracion_real = duracion_real
        sesion.estado = 'Completado' if completada else 'Cancelado'
        
        # Agregar calificación si se proporciona
        if calificacion is not None and 1 <= calificacion <= 5:
            calificacion_param = SesionTecnicaParam(
                sesion_id=sesion_id,
                codigo='calificacion',
                cantidad=str(calificacion)
            )
            db.session.add(calificacion_param)
        
        db.session.commit()
        
        # Obtener parámetros para la respuesta
        parametros = {p.codigo: p.cantidad for p in sesion.parametros}
        duracion_planificada = int(parametros.get('duracion_planificada', 0))
        tipo_meditacion = parametros.get('tipo_meditacion', 'mindfulness')
        
        return {
            'message': 'Meditación finalizada exitosamente',
            'sesion_id': sesion_id,
            'completada': completada,
            'duracion_planificada': duracion_planificada,
            'duracion_real': duracion_real,
            'tipo_meditacion': tipo_meditacion,
            'calificacion': calificacion,
            'porcentaje_completado': round((duracion_real / duracion_planificada) * 100, 2) if duracion_planificada > 0 else 0
        }
    
    @classmethod
    def obtener_tipos_meditacion(cls):
        """Obtiene los tipos de meditación disponibles"""
        return cls.TIPOS_MEDITACION
    
    @classmethod
    def obtener_historial_meditaciones(cls, usuario_id, limite=20):
        """Obtiene el historial de meditaciones del usuario"""
        
        # Obtener técnica de meditación
        tecnica_meditacion = Tecnica.query.filter_by(nombre='Meditación').first()
        if not tecnica_meditacion:
            return []
        
        sesiones = Sesion.query.filter_by(
            usuario_id=usuario_id,
            tecnica_id=tecnica_meditacion.tecnica_id
        ).order_by(Sesion.inicio.desc()).limit(limite).all()
        
        historial = []
        for sesion in sesiones:
            parametros = {p.codigo: p.cantidad for p in sesion.parametros}
            
            historial.append({
                'sesion_id': sesion.sesion_id,
                'fecha': sesion.inicio.date().isoformat(),
                'hora_inicio': sesion.inicio.time().strftime('%H:%M'),
                'duracion_real': sesion.duracion_real,
                'estado': sesion.estado,
                'tipo_meditacion': parametros.get('tipo_meditacion', 'mindfulness'),
                'calificacion': int(parametros['calificacion']) if parametros.get('calificacion') else None
            })
        
        return historial
    
    @classmethod
    def _formatear_respuesta_meditacion(cls, sesion):
        """Formatea la respuesta con información de la meditación"""
        parametros = {p.codigo: p.cantidad for p in sesion.parametros}
        
        ahora = datetime.utcnow()
        tiempo_transcurrido = (ahora - sesion.inicio).total_seconds() / 60
        
        return {
            'sesion_id': sesion.sesion_id,
            'estado': sesion.estado,
            'inicio': sesion.inicio.isoformat(),
            'duracion_planificada': int(parametros.get('duracion_planificada', 10)),
            'tipo_meditacion': parametros.get('tipo_meditacion', 'mindfulness'),
            'tiempo_transcurrido': round(tiempo_transcurrido, 2)
        }