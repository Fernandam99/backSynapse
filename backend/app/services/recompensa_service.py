# services/recompensa_service.py
from ..models import db, Recompensa, RecompensaUsuario, Usuario, Sesion, Tarea, SesionTecnicaParam
from datetime import datetime, date, timedelta
import json

class RecompensaService:
    
    # Niveles de recompensas
    NIVELES = {
        'BAJA': {'valor': 10, 'nombre': 'Bronce'},
        'MEDIA': {'valor': 25, 'nombre': 'Plata'}, 
        'ALTA': {'valor': 50, 'nombre': 'Oro'},
        'MUY_ALTA': {'valor': 100, 'nombre': 'Platino'}
    }
    
    @classmethod
    def inicializar_recompensas_sistema(cls):
        """Crea las recompensas base del sistema si no existen"""
        
        recompensas_base = [
            {
                'nombre': 'Meditador Principiante',
                'descripcion': 'Completa tu primera meditación',
                'tipo': 'puntos',
                'valor': cls.NIVELES['BAJA']['valor'],
                'requisitos': {'meditaciones_completadas': 1}
            },
            {
                'nombre': 'Organizador Eficiente',
                'descripcion': 'Completa una tarea en el tiempo asignado',
                'tipo': 'puntos',
                'valor': cls.NIVELES['MEDIA']['valor'],
                'requisitos': {'tareas_completadas_tiempo': 1}
            },
            {
                'nombre': 'Maestro del Pomodoro',
                'descripcion': 'Completa un ciclo completo de Pomodoro',
                'tipo': 'puntos',
                'valor': cls.NIVELES['ALTA']['valor'],
                'requisitos': {'pomodoros_completos': 1}
            },
            {
                'nombre': 'Productividad Extrema',
                'descripcion': 'Completa una tarea en la mitad del tiempo asignado',
                'tipo': 'puntos',
                'valor': cls.NIVELES['MUY_ALTA']['valor'],
                'requisitos': {'tareas_anticipadas_mitad_tiempo': 1}
            },
            {
                'nombre': 'Concentración Total',
                'descripcion': 'Completa un Pomodoro con modo no distracción activo',
                'tipo': 'puntos',
                'valor': cls.NIVELES['MUY_ALTA']['valor'],
                'requisitos': {'pomodoros_sin_distraccion': 1}
            }
        ]
        
        for recompensa_data in recompensas_base:
            existing = Recompensa.query.filter_by(nombre=recompensa_data['nombre']).first()
            if not existing:
                nueva_recompensa = Recompensa(
                    nombre=recompensa_data['nombre'],
                    descripcion=recompensa_data['descripcion'],
                    tipo=recompensa_data['tipo'],
                    valor=recompensa_data['valor'],
                    requisitos=recompensa_data['requisitos']
                )
                db.session.add(nueva_recompensa)
        
        db.session.commit()
    
    @classmethod
    def verificar_recompensas_meditacion(cls, usuario_id, sesion_id):
        """Verifica y otorga recompensas por completar meditación"""
        
        # Contar meditaciones completadas
        from backend.models import Tecnica
        
        tecnica_meditacion = Tecnica.query.filter_by(nombre='Meditación').first()
        if not tecnica_meditacion:
            return
        
        meditaciones_completadas = Sesion.query.filter_by(
            usuario_id=usuario_id,
            tecnica_id=tecnica_meditacion.tecnica_id,
            estado='Completado'
        ).count()
        
        # Verificar recompensa de primera meditación
        if meditaciones_completadas == 1:
            cls._otorgar_recompensa_por_tipo(usuario_id, 'meditaciones_completadas', 1)
        
        # Verificar recompensas por hitos de meditación
        hitos_meditacion = [5, 10, 25, 50, 100]
        for hito in hitos_meditacion:
            if meditaciones_completadas == hito:
                cls._crear_recompensa_hito_meditacion(hito)
                cls._otorgar_recompensa_por_tipo(usuario_id, 'meditaciones_completadas', hito)
    
    @classmethod
    def verificar_recompensas_tarea_completada(cls, usuario_id, tarea_id):
        """Verifica recompensas por completar tarea en tiempo"""
        
        tarea = Tarea.query.get(tarea_id)
        if not tarea or tarea.estado != 'Completado':
            return
        
        hoy = date.today()
        
        # Verificar si se completó a tiempo
        if tarea.fecha_vencimiento and hoy <= tarea.fecha_vencimiento:
            cls._otorgar_recompensa_por_tipo(usuario_id, 'tareas_completadas_tiempo', 1)
    
    @classmethod
    def verificar_recompensas_tarea_anticipada(cls, usuario_id, tarea_id):
        """Verifica recompensas por completar tarea anticipadamente"""
        
        tarea = Tarea.query.get(tarea_id)
        if not tarea or tarea.estado != 'Completado':
            return
        
        hoy = date.today()
        
        if tarea.fecha_vencimiento and hoy < tarea.fecha_vencimiento:
            dias_anticipados = (tarea.fecha_vencimiento - hoy).days
            tiempo_total = (tarea.fecha_vencimiento - tarea.fecha_creacion.date()).days
            
            # Si se completó en la mitad del tiempo o menos
            if tiempo_total > 0 and dias_anticipados >= (tiempo_total / 2):
                cls._otorgar_recompensa_por_tipo(usuario_id, 'tareas_anticipadas_mitad_tiempo', 1)
            else:
                # Recompensa normal por completar anticipadamente
                cls._otorgar_recompensa_por_tipo(usuario_id, 'tareas_completadas_tiempo', 1)
    
    @classmethod
    def verificar_recompensas_pomodoro(cls, usuario_id, sesion_id):
        """Verifica recompensas por ciclo de pomodoro"""
        # Esta se llama en cada ciclo completado, la recompensa principal se otorga al completar todo
        pass
    
    @classmethod
    def verificar_recompensas_pomodoro_completo(cls, usuario_id, sesion_id):
        """Verifica recompensas por completar pomodoro completo"""
        
        sesion = Sesion.query.get(sesion_id)
        if not sesion:
            return
        
        parametros = {p.codigo: p.cantidad for p in sesion.parametros}
        ciclos_completados = int(parametros.get('ciclos_completados', 0))
        ciclos_objetivo = int(parametros.get('ciclos_objetivo', 4))
        modo_no_distraccion = parametros.get('modo_no_distraccion', 'False') == 'True'
        
        # Verificar pomodoro completo
        if ciclos_completados >= ciclos_objetivo:
            cls._otorgar_recompensa_por_tipo(usuario_id, 'pomodoros_completos', 1)
            
            # Verificar recompensa especial por modo no distracción
            if modo_no_distraccion:
                cls._otorgar_recompensa_por_tipo(usuario_id, 'pomodoros_sin_distraccion', 1)
    
    @classmethod
    def verificar_todas_recompensas_usuario(cls, usuario_id):
        """Verifica todas las recompensas disponibles para un usuario"""
        
        # Asegurar que las recompensas base existan
        cls.inicializar_recompensas_sistema()
        
        stats = cls._obtener_estadisticas_usuario_para_recompensas(usuario_id)
        recompensas_otorgadas = []
        
        # Verificar cada tipo de recompensa
        tipos_verificacion = [
            'meditaciones_completadas',
            'tareas_completadas_tiempo', 
            'pomodoros_completos',
            'tareas_anticipadas_mitad_tiempo',
            'pomodoros_sin_distraccion'
        ]
        
        for tipo in tipos_verificacion:
            if stats.get(tipo, 0) > 0:
                recompensa = cls._otorgar_recompensa_por_tipo(usuario_id, tipo, stats[tipo])
                if recompensa:
                    recompensas_otorgadas.append(recompensa)
        
        return {
            'recompensas_otorgadas': recompensas_otorgadas,
            'estadisticas_usuario': stats
        }
    
    @classmethod
    def obtener_niveles_recompensas(cls):
        """Obtiene información sobre los niveles de recompensas"""
        return cls.NIVELES
    
    @classmethod
    def obtener_estadisticas_usuario(cls, usuario_id):
        """Obtiene estadísticas completas del usuario para recompensas"""
        
        stats = cls._obtener_estadisticas_usuario_para_recompensas(usuario_id)
        
        # Obtener recompensas del usuario
        recompensas_usuario = RecompensaUsuario.query.filter_by(usuario_id=usuario_id).count()
        puntos_totales = db.session.query(
            db.func.sum(Recompensa.valor)
        ).join(RecompensaUsuario).filter(
            RecompensaUsuario.usuario_id == usuario_id
        ).scalar() or 0
        
        return {
            'estadisticas_actividades': stats,
            'recompensas': {
                'total_recompensas': recompensas_usuario,
                'puntos_totales': puntos_totales,
                'nivel_usuario': cls._calcular_nivel_usuario(puntos_totales)
            }
        }
    
    @classmethod
    def _obtener_estadisticas_usuario_para_recompensas(cls, usuario_id):
        """Obtiene estadísticas específicas para verificar recompensas"""
        
        # Meditaciones completadas
        from backend.models import Tecnica
        tecnica_meditacion = Tecnica.query.filter_by(nombre='Meditación').first()
        meditaciones_completadas = 0
        if tecnica_meditacion:
            meditaciones_completadas = Sesion.query.filter_by(
                usuario_id=usuario_id,
                tecnica_id=tecnica_meditacion.tecnica_id,
                estado='Completado'
            ).count()
        
        # Pomodoros completados
        tecnica_pomodoro = Tecnica.query.filter_by(nombre='Pomodoro').first()
        pomodoros_completos = 0
        pomodoros_sin_distraccion = 0
        
        if tecnica_pomodoro:
            sesiones_pomodoro = Sesion.query.filter_by(
                usuario_id=usuario_id,
                tecnica_id=tecnica_pomodoro.tecnica_id,
                estado='Completado'
            ).all()
            
            for sesion in sesiones_pomodoro:
                parametros = {p.codigo: p.cantidad for p in sesion.parametros}
                ciclos_completados = int(parametros.get('ciclos_completados', 0))
                ciclos_objetivo = int(parametros.get('ciclos_objetivo', 4))
                modo_no_distraccion = parametros.get('modo_no_distraccion', 'False') == 'True'
                
                if ciclos_completados >= ciclos_objetivo:
                    pomodoros_completos += 1
                    if modo_no_distraccion:
                        pomodoros_sin_distraccion += 1
        
        # Tareas completadas a tiempo y anticipadas
        hoy = date.today()
        tareas_completadas_tiempo = Tarea.query.filter(
            Tarea.usuario_id == usuario_id,
            Tarea.estado == 'Completado',
            Tarea.fecha_vencimiento >= hoy
        ).count()
        
        tareas_anticipadas_mitad_tiempo = Tarea.query.filter(
            Tarea.usuario_id == usuario_id,
            Tarea.estado == 'Completado',
            Tarea.comentario.like('%días antes de tiempo%')
        ).count()
        
        return {
            'meditaciones_completadas': meditaciones_completadas,
            'pomodoros_completos': pomodoros_completos,
            'pomodoros_sin_distraccion': pomodoros_sin_distraccion,
            'tareas_completadas_tiempo': tareas_completadas_tiempo,
            'tareas_anticipadas_mitad_tiempo': tareas_anticipadas_mitad_tiempo
        }
    
    @classmethod
    def _otorgar_recompensa_por_tipo(cls, usuario_id, tipo_requisito, cantidad):
        """Otorga recompensa basada en tipo de logro"""
        
        # Buscar recompensa que coincida con el tipo
        recompensas_aplicables = Recompensa.query.all()
        
        for recompensa in recompensas_aplicables:
            if tipo_requisito in recompensa.requisitos:
                valor_requerido = recompensa.requisitos[tipo_requisito]
                
                # Verificar si el usuario ya tiene esta recompensa
                ya_tiene = RecompensaUsuario.query.filter_by(
                    usuario_id=usuario_id,
                    recompensa_id=recompensa.recompensa_id
                ).first()
                
                if not ya_tiene and cantidad >= valor_requerido:
                    # Otorgar recompensa
                    nueva_recompensa_usuario = RecompensaUsuario(
                        usuario_id=usuario_id,
                        recompensa_id=recompensa.recompensa_id
                    )
                    
                    db.session.add(nueva_recompensa_usuario)
                    db.session.commit()
                    
                    return {
                        'recompensa_id': recompensa.recompensa_id,
                        'nombre': recompensa.nombre,
                        'descripcion': recompensa.descripcion,
                        'valor': recompensa.valor
                    }
        
        return None
    
    @classmethod
    def _crear_recompensa_hito_meditacion(cls, hito):
        """Crea recompensas por hitos de meditación si no existen"""
        
        nombre = f'Meditador {cls._obtener_titulo_hito(hito)}'
        existing = Recompensa.query.filter_by(nombre=nombre).first()
        
        if not existing:
            valor = cls._calcular_valor_hito(hito)
            nueva_recompensa = Recompensa(
                nombre=nombre,
                descripcion=f'Completa {hito} meditaciones',
                tipo='puntos',
                valor=valor,
                requisitos={'meditaciones_completadas': hito}
            )
            db.session.add(nueva_recompensa)
            db.session.commit()
    
    @classmethod
    def _obtener_titulo_hito(cls, hito):
        """Obtiene título según el hito alcanzado"""
        titulos = {
            5: 'Dedicado',
            10: 'Persistente', 
            25: 'Experto',
            50: 'Maestro',
            100: 'Guru'
        }
        return titulos.get(hito, 'Avanzado')
    
    @classmethod
    def _calcular_valor_hito(cls, hito):
        """Calcula valor de recompensa según el hito"""
        if hito <= 5:
            return cls.NIVELES['BAJA']['valor']
        elif hito <= 15:
            return cls.NIVELES['MEDIA']['valor']
        elif hito <= 50:
            return cls.NIVELES['ALTA']['valor']
        else:
            return cls.NIVELES['MUY_ALTA']['valor']
    
    @classmethod
    def _calcular_nivel_usuario(cls, puntos_totales):
        """Calcula el nivel del usuario basado en puntos totales"""
        if puntos_totales < 100:
            return 'Principiante'
        elif puntos_totales < 300:
            return 'Intermedio'
        elif puntos_totales < 600:
            return 'Avanzado'
        elif puntos_totales < 1000:
            return 'Experto'
        else:
            return 'Maestro'