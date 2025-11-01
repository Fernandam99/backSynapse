from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, Recompensa, RecompensaUsuario, Usuario
import json

recompensa_bp = Blueprint('recompensa', __name__)

@recompensa_bp.route('', methods=['GET'])
@jwt_required()
def get_recompensas():
    try:
        tipo = request.args.get('tipo')
        
        if tipo:
            recompensas = Recompensa.query.filter_by(tipo=tipo).all()
        else:
            recompensas = Recompensa.query.all()
        
        return jsonify([recompensa.to_dict() for recompensa in recompensas]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@recompensa_bp.route('/<string:recompensa_id>', methods=['GET'])
@jwt_required()
def get_recompensa(recompensa_id):
    try:
        recompensa = Recompensa.query.get(recompensa_id)
        if not recompensa:
            return jsonify({'error': 'Recompensa no encontrada'}), 404
        
        return jsonify(recompensa.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@recompensa_bp.route('', methods=['POST'])
@jwt_required()
def create_recompensa():
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        if not data.get('nombre') or not data.get('valor') or not data.get('requisitos'):
            return jsonify({'error': 'Nombre, valor y requisitos son requeridos'}), 400
        
        # Validar que requisitos sea un objeto JSON válido
        try:
            requisitos = data['requisitos'] if isinstance(data['requisitos'], dict) else json.loads(data['requisitos'])
        except (json.JSONDecodeError, TypeError):
            return jsonify({'error': 'Requisitos debe ser un objeto JSON válido'}), 400
        
        # Crear nueva recompensa
        nueva_recompensa = Recompensa(
            nombre=data['nombre'],
            descripcion=data.get('descripcion'),
            tipo=data.get('tipo', 'puntos'),
            valor=data['valor'],
            requisitos=requisitos
        )
        
        db.session.add(nueva_recompensa)
        db.session.commit()
        
        return jsonify(nueva_recompensa.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@recompensa_bp.route('/<string:recompensa_id>', methods=['PUT'])
@jwt_required()
def update_recompensa(recompensa_id):
    try:
        recompensa = Recompensa.query.get(recompensa_id)
        if not recompensa:
            return jsonify({'error': 'Recompensa no encontrada'}), 404
        
        data = request.get_json()
        
        # Actualizar campos permitidos
        if 'nombre' in data:
            recompensa.nombre = data['nombre']
        if 'descripcion' in data:
            recompensa.descripcion = data['descripcion']
        if 'tipo' in data and data['tipo'] in ['personalizacion', 'tecnica', 'puntos']:
            recompensa.tipo = data['tipo']
        if 'valor' in data:
            recompensa.valor = data['valor']
        
        if 'requisitos' in data:
            try:
                requisitos = data['requisitos'] if isinstance(data['requisitos'], dict) else json.loads(data['requisitos'])
                recompensa.requisitos = requisitos
            except (json.JSONDecodeError, TypeError):
                return jsonify({'error': 'Requisitos debe ser un objeto JSON válido'}), 400
        
        db.session.commit()
        
        return jsonify(recompensa.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@recompensa_bp.route('/<string:recompensa_id>', methods=['DELETE'])
@jwt_required()
def delete_recompensa(recompensa_id):
    try:
        recompensa = Recompensa.query.get(recompensa_id)
        if not recompensa:
            return jsonify({'error': 'Recompensa no encontrada'}), 404
        
        
        db.session.delete(recompensa)
        db.session.commit()
        
        return jsonify({'message': 'Recompensa eliminada exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@recompensa_bp.route('/mis-recompensas', methods=['GET'])
@jwt_required()
def get_mis_recompensas():
    try:
        id_usuario = get_jwt_identity()
        
        # Obtener recompensas del usuario
        recompensas_usuario = db.session.query(
            RecompensaUsuario, Recompensa
        ).join(Recompensa).filter(
            RecompensaUsuario.id_usuario == id_usuario  
        ).order_by(RecompensaUsuario.fecha_obtenida.desc()).all()
        
        resultado = []
        for recompensa_usuario, recompensa in recompensas_usuario:
            recompensa_dict = recompensa.to_dict()
            recompensa_dict.update({
                'fecha_obtenida': recompensa_usuario.fecha_obtenida.isoformat(),
                'consumida': recompensa_usuario.consumida,
                'recompensa_id_usuario': recompensa_usuario.id_usuario  # Corregido el campo
            })
            resultado.append(recompensa_dict)
        
        return jsonify(resultado), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Definir la función calcular_progreso_requisitos
def calcular_progreso_requisitos(requisitos, stats_usuario):
    """Calcula el progreso del usuario hacia los requisitos de una recompensa"""
    progreso = {}
    try:
        for key, valor_requerido in requisitos.items():
            if key in stats_usuario:
                actual = stats_usuario[key]
                porcentaje = min(100, (actual / valor_requerido) * 100) if valor_requerido > 0 else 100
                progreso[key] = {
                    'actual': actual,
                    'requerido': valor_requerido,
                    'porcentaje': round(porcentaje, 2)
                }
        return progreso
    except Exception as e:
        return {}

# Asegúrate de que ambas funciones estén definidas o importadas
def evaluar_requisitos(requisitos, stats_usuario):
    """Evalúa si el usuario cumple con los requisitos para una recompensa"""
    try:
        for key, valor_requerido in requisitos.items():
            if key in stats_usuario:
                if stats_usuario[key] < valor_requerido:
                    return False
        return True
    except Exception as e:
        return False

# Código de la ruta GET /disponibles
@recompensa_bp.route('/disponibles', methods=['GET'])
@jwt_required()
def get_recompensas_disponibles():
    try:
        id_usuario = get_jwt_identity()

        # Obtener estadísticas del usuario para evaluar requisitos
        from app.models import Sesion, Tarea, Progreso
        
        # Sesiones completadas
        sesiones_completadas = Sesion.query.filter_by(
            usuario_id=id_usuario, 
            estado='Completado'
        ).count()
        
        # Tareas completadas
        tareas_completadas = Tarea.query.filter_by(
            usuario_id=id_usuario,  # Corregido el campo
            estado='Completado'
        ).count()
        
        # Tiempo total de estudio
        tiempo_total = db.session.query(
            db.func.sum(Sesion.duracion_real)
        ).filter_by(usuario_id=id_usuario, estado='Completado').scalar() or 0
        
        # Días consecutivos (simplificado)
        dias_consecutivos = Progreso.query.filter_by(usuario_id=id_usuario).count()
        
        # Recompensas ya obtenidas
        recompensas_obtenidas = db.session.query(RecompensaUsuario.id_recompensa).filter_by(
            id_usuario=id_usuario
        ).subquery()
        
        # Recompensas disponibles (no obtenidas)
        recompensas_disponibles = Recompensa.query.filter(
            ~Recompensa.id_recompensa.in_(recompensas_obtenidas)
        ).all()
        
        # Evaluar cuáles puede obtener
        resultado = []
        stats_usuario = {
            'sesiones_completadas': sesiones_completadas,
            'tareas_completadas': tareas_completadas,
            'tiempo_total_minutos': tiempo_total,
            'dias_consecutivos': dias_consecutivos
        }
        
        for recompensa in recompensas_disponibles:
            recompensa_dict = recompensa.to_dict()
            puede_obtener = evaluar_requisitos(recompensa.requisitos, stats_usuario)  # type: ignore
            recompensa_dict['puede_obtener'] = puede_obtener
            recompensa_dict['progreso_requisitos'] = calcular_progreso_requisitos(recompensa.requisitos, stats_usuario) # type: ignore
            resultado.append(recompensa_dict)
        
        return jsonify(resultado), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    
@recompensa_bp.route('/consumir', methods=['POST'])
@jwt_required()
def consumir_recompensa():
    try:
        data = request.get_json()
        id_usuario = get_jwt_identity()

        id_recompensa = data.get('recompensa_id')
        if not id_recompensa:
            return jsonify({'error': 'ID de recompensa es requerido'}), 400

        # Buscar si el usuario tiene esa recompensa
        recompensa_usuario = RecompensaUsuario.query.filter_by(
            id_usuario=id_usuario,
            id_recompensa=id_recompensa
        ).first()

        if not recompensa_usuario:
            return jsonify({'error': 'No tienes esta recompensa o ya fue consumida'}), 404

        # marcar como consumida
        recompensa_usuario.consumida = True
        db.session.commit()

        return jsonify({'message': 'Recompensa consumida correctamente'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500



@recompensa_bp.route('/consumir/<string:recompensa_id_usuario>', methods=['PATCH'])
@jwt_required()
def consumir_recompensa_patch(recompensa_id_usuario):
    try:
        id_usuario = get_jwt_identity()
        
        recompensa_usuario = RecompensaUsuario.query.filter_by(
            id=recompensa_id_usuario,  # Usando el nombre correcto para el parámetro
            id_usuario=id_usuario
        ).first()
        
        if not recompensa_usuario:
            return jsonify({'error': 'Recompensa no encontrada'}), 404
        
        if recompensa_usuario.consumida:
            return jsonify({'error': 'Esta recompensa ya ha sido consumida'}), 400
        
        recompensa_usuario.consumida = True
        db.session.commit()
        
        return jsonify({'message': 'Recompensa consumida exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
