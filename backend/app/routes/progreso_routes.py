from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, Progreso, Sesion, Tarea
from datetime import datetime, date, timedelta
from sqlalchemy import func

progreso_bp = Blueprint('progreso', __name__)

@progreso_bp.route('', methods=['GET'])
@jwt_required()
def get_progreso():
    try:
        usuario_id = get_jwt_identity()
        
        # Parámetros opcionales
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        query = Progreso.query.filter_by(usuario_id=usuario_id)
        
        if fecha_inicio:
            try:
                fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                query = query.filter(Progreso.fecha >= fecha_inicio_dt)
            except ValueError:
                return jsonify({'error': 'Formato de fecha_inicio inválido (YYYY-MM-DD)'}), 400
        
        if fecha_fin:
            try:
                fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
                query = query.filter(Progreso.fecha <= fecha_fin_dt)
            except ValueError:
                return jsonify({'error': 'Formato de fecha_fin inválido (YYYY-MM-DD)'}), 400
        
        progreso = query.order_by(Progreso.fecha.desc()).all()
        
        return jsonify([p.to_dict() for p in progreso]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@progreso_bp.route('/hoy', methods=['GET'])
@jwt_required()
def get_progreso_hoy():
    try:
        usuario_id = get_jwt_identity()
        hoy = date.today()
        
        progreso_hoy = Progreso.query.filter_by(
            usuario_id=usuario_id,
            fecha=hoy
        ).first()
        
        if not progreso_hoy:
            # Crear registro de progreso para hoy si no existe
            progreso_hoy = Progreso(
                usuario_id=usuario_id,
                fecha=hoy,
                minutos_estudio=0,
                tareas_completadas=0,
                sesiones_realizadas=0
            )
            db.session.add(progreso_hoy)
            db.session.commit()
        
        return jsonify(progreso_hoy.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@progreso_bp.route('/actualizar', methods=['POST'])
@jwt_required()
def actualizar_progreso():
    try:
        usuario_id = get_jwt_identity()
        hoy = date.today()
        
        # Calcular estadísticas del día actual
        minutos_estudio = db.session.query(
            func.sum(Sesion.duracion_real)
        ).filter(
            Sesion.usuario_id == usuario_id,
            func.date(Sesion.fecha_inicio) == hoy,  # Cambié 'inicio' por 'fecha_inicio'
            Sesion.estado == 'Completado'
        ).scalar() or 0
        
        tareas_completadas = Tarea.query.filter(
            Tarea.usuario_id == usuario_id,
            func.date(Tarea.fecha_creacion) == hoy,
            Tarea.estado == 'Completado'
        ).count()
        
        sesiones_realizadas = Sesion.query.filter(
            Sesion.usuario_id == usuario_id,
            func.date(Sesion.fecha_inicio) == hoy,  # Cambié 'inicio' por 'fecha_inicio'
            Sesion.estado == 'Completado'
        ).count()
        
        # Buscar o crear registro de progreso
        progreso = Progreso.query.filter_by(
            usuario_id=usuario_id,
            fecha=hoy
        ).first()
        
        if progreso:
            progreso.minutos_estudio = minutos_estudio
            progreso.tareas_completadas = tareas_completadas
            progreso.sesiones_realizadas = sesiones_realizadas
        else:
            progreso = Progreso(
                usuario_id=usuario_id,
                fecha=hoy,
                minutos_estudio=minutos_estudio,
                tareas_completadas=tareas_completadas,
                sesiones_realizadas=sesiones_realizadas
            )
            db.session.add(progreso)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Progreso actualizado exitosamente',
            'progreso': progreso.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@progreso_bp.route('/semana', methods=['GET'])
@jwt_required()
def get_progreso_semana():
    try:
        usuario_id = get_jwt_identity()
        hoy = date.today()
        inicio_semana = hoy - timedelta(days=hoy.weekday())  # Lunes
        fin_semana = inicio_semana + timedelta(days=6)  # Domingo
        
        # Obtener progreso de la semana
        progreso_semana = Progreso.query.filter(
            Progreso.usuario_id == usuario_id,
            Progreso.fecha >= inicio_semana,
            Progreso.fecha <= fin_semana
        ).order_by(Progreso.fecha).all()
        
        # Crear estructura completa de la semana (7 días)
        dias_semana = []
        for i in range(7):
            fecha_dia = inicio_semana + timedelta(days=i)
            progreso_dia = next((p for p in progreso_semana if p.fecha == fecha_dia), None)
            
            if progreso_dia:
                dias_semana.append(progreso_dia.to_dict())
            else:
                dias_semana.append({
                    'progreso_id': None,
                    'usuario_id': usuario_id,
                    'fecha': fecha_dia.isoformat(),
                    'minutos_estudio': 0,
                    'tareas_completadas': 0,
                    'sesiones_realizadas': 0
                })
        
        # Calcular totales de la semana
        total_minutos = sum(dia['minutos_estudio'] for dia in dias_semana)
        total_tareas = sum(dia['tareas_completadas'] for dia in dias_semana)
        total_sesiones = sum(dia['sesiones_realizadas'] for dia in dias_semana)
        
        return jsonify({
            'inicio_semana': inicio_semana.isoformat(),
            'fin_semana': fin_semana.isoformat(),
            'dias': dias_semana,
            'totales': {
                'minutos_estudio': total_minutos,
                'horas_estudio': round(total_minutos / 60, 2),
                'tareas_completadas': total_tareas,
                'sesiones_realizadas': total_sesiones
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@progreso_bp.route('/mes', methods=['GET'])
@jwt_required()
def get_progreso_mes():
    try:
        usuario_id = get_jwt_identity()
        
        # Obtener año y mes (por defecto el actual)
        año = int(request.args.get('año', datetime.now().year))
        mes = int(request.args.get('mes', datetime.now().month))
        
        # Primer y último día del mes
        primer_dia = date(año, mes, 1)
        if mes == 12:
            ultimo_dia = date(año + 1, 1, 1) - timedelta(days=1)
        else:
            ultimo_dia = date(año, mes + 1, 1) - timedelta(days=1)
        
        # Obtener progreso del mes
        progreso_mes = Progreso.query.filter(
            Progreso.usuario_id == usuario_id,
            Progreso.fecha >= primer_dia,
            Progreso.fecha <= ultimo_dia
        ).order_by(Progreso.fecha).all()
        
        # Calcular estadísticas del mes
        total_minutos = sum(p.minutos_estudio for p in progreso_mes)
        total_tareas = sum(p.tareas_completadas for p in progreso_mes)
        total_sesiones = sum(p.sesiones_realizadas for p in progreso_mes)
        dias_activos = len([p for p in progreso_mes if p.minutos_estudio > 0 or p.sesiones_realizadas > 0])
        
        # Promedio diario
        dias_en_mes = (ultimo_dia - primer_dia).days + 1
        promedio_minutos = total_minutos / dias_en_mes if dias_en_mes > 0 else 0
        
        return jsonify({
            'año': año,
            'mes': mes,
            'primer_dia': primer_dia.isoformat(),
            'ultimo_dia': ultimo_dia.isoformat(),
            'progreso_diario': [p.to_dict() for p in progreso_mes],
            'estadisticas': {
                'total_minutos': total_minutos,
                'total_horas': round(total_minutos / 60, 2),
                'total_tareas': total_tareas,
                'total_sesiones': total_sesiones,
                'dias_activos': dias_activos,
                'dias_en_mes': dias_en_mes,
                'promedio_minutos_dia': round(promedio_minutos, 2),
                'racha_dias': calcular_racha_dias(progreso_mes)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@progreso_bp.route('/estadisticas-generales', methods=['GET'])
@jwt_required()
def get_estadisticas_generales():
    try:
        usuario_id = get_jwt_identity()
        
        # Estadísticas de todas las sesiones
        total_sesiones = Sesion.query.filter_by(
            usuario_id=usuario_id, 
            estado='Completado'
        ).count()
        
        tiempo_total = db.session.query(
            func.sum(Sesion.duracion_real)
        ).filter_by(usuario_id=usuario_id, estado='Completado').scalar() or 0
        
        # Estadísticas de tareas
        total_tareas = Tarea.query.filter_by(usuario_id=usuario_id).count()
        tareas_completadas = Tarea.query.filter_by(
            usuario_id=usuario_id, 
            estado='Completado'
        ).count()
        
        # Racha actual de días estudiando
        progreso_reciente = Progreso.query.filter_by(
            usuario_id=usuario_id
        ).order_by(Progreso.fecha.desc()).limit(30).all()
        
        racha_actual = calcular_racha_actual(progreso_reciente)
        
        # Día con más minutos de estudio
        mejor_dia = Progreso.query.filter_by(
            usuario_id=usuario_id
        ).order_by(Progreso.minutos_estudio.desc()).first()
        
        # Técnica más utilizada
        tecnica_favorita = db.session.query(
            func.count(Sesion.id_sesion).label('total'),
            Sesion.tecnica_id
        ).filter_by(usuario_id=usuario_id).group_by(
            Sesion.tecnica_id
        ).order_by(db.desc('total')).first()
        
        tecnica_nombre = None
        if tecnica_favorita:
            from models import Tecnica
            tecnica = Tecnica.query.get(tecnica_favorita.tecnica_id)
            tecnica_nombre = tecnica.nombre if tecnica else None
        
        return jsonify({
            'sesiones': {
                'total': total_sesiones,
                'tiempo_total_minutos': tiempo_total,
                'tiempo_total_horas': round(tiempo_total / 60, 2),
                'promedio_duracion': round(tiempo_total / total_sesiones, 2) if total_sesiones > 0 else 0
            },
            'tareas': {
                'total': total_tareas,
                'completadas': tareas_completadas,
                'porcentaje_completadas': round((tareas_completadas / total_tareas) * 100, 2) if total_tareas > 0 else 0
            },
            'racha_dias_actual': racha_actual,
            'mejor_dia': {
                'fecha': mejor_dia.fecha.isoformat() if mejor_dia else None,
                'minutos': mejor_dia.minutos_estudio if mejor_dia else 0
            },
            'tecnica_favorita': tecnica_nombre,
            'total_dias_registrados': Progreso.query.filter_by(usuario_id=usuario_id).count()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def calcular_racha_dias(progreso_mes):
    """Calcula la racha de días consecutivos con actividad"""
    if not progreso_mes:
        return 0
    
    racha_maxima = 0
    racha_actual = 0
    
    for p in progreso_mes:
        if p.minutos_estudio > 0 or p.sesiones_realizadas > 0:
            racha_actual += 1
            racha_maxima = max(racha_maxima, racha_actual)
        else:
            racha_actual = 0
    
    return racha_maxima

def calcular_racha_actual(progreso_reciente):
    """Calcula la racha actual de días consecutivos"""
    if not progreso_reciente:
        return 0
    
    # Ordenar por fecha descendente
    progreso_ordenado = sorted(progreso_reciente, key=lambda x: x.fecha, reverse=True)
    
    racha = 0
    fecha_esperada = date.today()
    
    for p in progreso_ordenado:
        if p.fecha == fecha_esperada and (p.minutos_estudio > 0 or p.sesiones_realizadas > 0):
            racha += 1
            fecha_esperada = fecha_esperada - timedelta(days=1)
        else:
            break
    
    return racha