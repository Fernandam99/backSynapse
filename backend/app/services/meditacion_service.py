# services/meditacion_service.py
from app.models import db, Sesion, Tecnica, SesionTecnicaParam
from datetime import datetime
import uuid

class MeditacionService:
    TIPOS_MEDITACION = [
        {'id': 'mindfulness', 'nombre': 'Mindfulness', 'descripcion': 'Meditación de atención plena'},
        {'id': 'respiracion', 'nombre': 'Respiración', 'descripcion': 'Enfoque en la respiración'},
        {'id': 'body_scan', 'nombre': 'Body Scan', 'descripcion': 'Exploración corporal'},
        {'id': 'loving_kindness', 'nombre': 'Amor y Bondad', 'descripcion': 'Cultivo de compasión'},
        {'id': 'concentracion', 'nombre': 'Concentración', 'descripcion': 'Enfoque en un objeto específico'}
    ]

    @classmethod
    def es_tipo_valido(cls, tipo_meditacion):
        """Verifica si el tipo de meditación es válido."""
        return any(tipo['id'] == tipo_meditacion for tipo in cls.TIPOS_MEDITACION)

    @classmethod
    def iniciar_meditacion(cls, usuario_id, duracion, tipo_meditacion='mindfulness'):
        """
        DEPRECATED: Ya no se usa para crear sesión en DB.
        Este método se mantiene por compatibilidad si otros servicios lo usan,
        pero no debería crear una sesión activa en la base de datos en este nuevo enfoque.
        """
        # Opcional: Validar tipo de meditación
        if not cls.es_tipo_valido(tipo_meditacion):
            raise ValueError("Tipo de meditación no válido")
        # Simplemente devolver datos iniciales o mensaje de confirmación
        return {
            'message': 'Inicio de meditación confirmado en frontend',
            'duracion': duracion,
            'tipo_meditacion': tipo_meditacion
        }

    @classmethod
    def guardar_sesion_finalizada(cls, usuario_id, tecnica_id, duracion_planificada, duracion_real, tipo_meditacion, estado, calificacion=None):
        """
        Crea una nueva sesión de meditación en la base de datos con sus parámetros.
        """
        # Validar tipo de meditación
        if not cls.es_tipo_valido(tipo_meditacion):
            raise ValueError("Tipo de meditación no válido")

        # Validar técnica (opcional, pero recomendable)
        tecnica = Tecnica.query.get(tecnica_id)
        if not tecnica:
            raise ValueError("Técnica no encontrada")

        # Calcular fecha_inicio basada en duracion_real y estado
        # Opcional: recibir fecha_inicio desde el frontend si es más preciso
        # Por ahora, asumimos que la sesión acaba de terminar
        fecha_fin = datetime.utcnow()
        fecha_inicio = fecha_fin - timedelta(minutes=duracion_real)

        # Crear sesión
        nueva_sesion = Sesion(
            usuario_id=usuario_id,
            tecnica_id=tecnica_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            duracion_real=duracion_real,
            estado=estado
            # es_grupal se asume False para meditación individual
        )
        db.session.add(nueva_sesion)
        db.session.flush() # flush para obtener el id_sesion antes de usarlo

        # Agregar parámetros específicos de la meditación
        parametros = [
            {'parametro': 'duracion_planificada', 'valor': str(duracion_planificada)},
            {'parametro': 'duracion_real', 'valor': str(duracion_real)},
            {'parametro': 'tipo_meditacion', 'valor': tipo_meditacion},
            {'parametro': 'tiempo_inicio', 'valor': fecha_inicio.isoformat()},
            {'parametro': 'tiempo_fin', 'valor': fecha_fin.isoformat()}
        ]
        if calificacion is not None and 1 <= calificacion <= 5:
             parametros.append({'parametro': 'calificacion', 'valor': str(calificacion)})

        for param in parametros:
            sesion_param = SesionTecnicaParam(
                id_sesion=nueva_sesion.id_sesion,
                parametro=param['parametro'],
                valor=param['valor']
            )
            db.session.add(sesion_param)

        db.session.commit()
        return cls._formatear_respuesta_guardar(nueva_sesion, calificacion)

    @classmethod
    def _formatear_respuesta_guardar(cls, sesion, calificacion=None):
        """Formatea la respuesta después de guardar la sesión."""
        parametros = {p.parametro: p.valor for p in sesion.parametros}
        duracion_planificada = int(parametros.get('duracion_planificada', 0))
        duracion_real = int(parametros.get('duracion_real', 0))
        tipo_meditacion = parametros.get('tipo_meditacion', 'mindfulness')

        return {
            'sesion_id': sesion.id_sesion,
            'usuario_id': sesion.usuario_id,
            'tecnica_id': sesion.tecnica_id,
            'fecha_inicio': sesion.fecha_inicio.isoformat(),
            'fecha_fin': sesion.fecha_fin.isoformat(),
            'duracion_planificada': duracion_planificada,
            'duracion_real': duracion_real,
            'tipo_meditacion': tipo_meditacion,
            'estado': sesion.estado,
            'calificacion': calificacion,
            'porcentaje_completado': round((duracion_real / duracion_planificada * 100), 2) if duracion_planificada > 0 else 0
        }

    # --- Métodos existentes que no cambian ---
    @classmethod
    def finalizar_meditacion(cls, usuario_id, sesion_id, completada=True, calificacion=None):
        """DEPRECATED en este enfoque."""
        # Este método ya no debería usarse si la sesión se crea directamente como finalizada
        pass

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
            tecnica_id=tecnica_meditacion.id_tecnica
        ).order_by(Sesion.fecha_inicio.desc()).limit(limite).all()

        historial = []
        for sesion in sesiones:
            parametros = {p.parametro: p.valor for p in sesion.parametros}
            historial.append({
                'sesion_id': sesion.id_sesion,
                'fecha': sesion.fecha_inicio.date().isoformat(),
                'hora_inicio': sesion.fecha_inicio.time().strftime('%H:%M'),
                'duracion_real': sesion.duracion_real,
                'estado': sesion.estado,
                'tipo_meditacion': parametros.get('tipo_meditacion', 'mindfulness'),
                'calificacion': int(parametros['calificacion']) if parametros.get('calificacion') else None
            })
        return historial

    @classmethod
    def _formatear_respuesta_meditacion(cls, sesion):
        """DEPRECATED en este enfoque."""
        # Este método ya no debería usarse
        pass
