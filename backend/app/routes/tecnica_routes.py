from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models import db, Tecnica

tecnica_bp = Blueprint('tecnica', __name__)

@tecnica_bp.route('', methods=['GET'])
@jwt_required()
def get_tecnicas():
    try:
        categoria = request.args.get('categoria')
        
        if categoria:
            tecnicas = Tecnica.query.filter_by(categoria=categoria).all()
        else:
            tecnicas = Tecnica.query.all()
        
        return jsonify([tecnica.to_dict() for tecnica in tecnicas]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@tecnica_bp.route('/populares', methods=['GET'])
@jwt_required()
def get_tecnicas_populares():
    try:
        # Obtener técnicas más usadas (basado en número de sesiones)
        from app.models import Sesion
        
        tecnicas_populares = db.session.query(
            Tecnica, 
            db.func.count(Sesion.id_sesion).label('total_sesiones')  # Corregir aquí
        ).outerjoin(Sesion).group_by(Tecnica.id_tecnica).order_by(
            db.desc('total_sesiones')
        ).limit(10).all()
        
        # Si no hay técnicas populares, se devuelve un mensaje adecuado
        if not tecnicas_populares:
            return jsonify({'message': 'No hay técnicas populares en este momento'}), 200
        
        result = []
        for tecnica, total_sesiones in tecnicas_populares:
            tecnica_dict = tecnica.to_dict()
            tecnica_dict['total_sesiones'] = total_sesiones
            result.append(tecnica_dict)
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@tecnica_bp.route('/<string:tecnica_id>', methods=['GET'])
@jwt_required()
def get_tecnica(tecnica_id):
    try:
        tecnica = Tecnica.query.get(tecnica_id)
        if not tecnica:
            return jsonify({'error': 'Técnica no encontrada'}), 404
        
        return jsonify(tecnica.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tecnica_bp.route('', methods=['POST'])
@jwt_required()
def create_tecnica():
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        if not data.get('nombre'):
            return jsonify({'error': 'El nombre de la técnica es requerido'}), 400
        
        # Verificar que no exista una técnica con el mismo nombre
        if Tecnica.query.filter_by(nombre=data['nombre']).first():
            return jsonify({'error': 'Ya existe una técnica con este nombre'}), 400
        
        # Crear nueva técnica
        nueva_tecnica = Tecnica(
            nombre=data['nombre'],
            categoria=data.get('categoria')
        )
        
        db.session.add(nueva_tecnica)
        db.session.commit()
        
        return jsonify(nueva_tecnica.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@tecnica_bp.route('/<string:tecnica_id>', methods=['PUT'])
@jwt_required()
def update_tecnica(tecnica_id):
    try:
        tecnica = Tecnica.query.get(tecnica_id)
        if not tecnica:
            return jsonify({'error': 'Técnica no encontrada'}), 404
        
        data = request.get_json()
        
        # Verificar nombre único si se está actualizando
        if 'nombre' in data and data['nombre'] != tecnica.nombre:
            if Tecnica.query.filter_by(nombre=data['nombre']).first():
                return jsonify({'error': 'Ya existe una técnica con este nombre'}), 400
            tecnica.nombre = data['nombre']
        
        if 'categoria' in data:
            tecnica.categoria = data['categoria']
        
        db.session.commit()
        
        return jsonify(tecnica.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@tecnica_bp.route('/<string:tecnica_id>', methods=['DELETE'])
@jwt_required()
def delete_tecnica(tecnica_id):
    try:
        tecnica = Tecnica.query.get(tecnica_id)
        if not tecnica:
            return jsonify({'error': 'Técnica no encontrada'}), 404
        
        # Verificar si la técnica está siendo usada en sesiones
        if tecnica.sesiones:
            return jsonify({'error': 'No se puede eliminar una técnica que tiene sesiones asociadas'}), 400
        
        db.session.delete(tecnica)
        db.session.commit()
        
        return jsonify({'message': 'Técnica eliminada exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@tecnica_bp.route('/categorias', methods=['GET'])
@jwt_required()
def get_categorias():
    try:
        # Obtener todas las categorías únicas
        categorias = db.session.query(Tecnica.categoria).distinct().filter(
            Tecnica.categoria.isnot(None)
        ).all()
        
        # Convertir a lista simple
        categorias_list = [cat[0] for cat in categorias if cat[0]]
        
        return jsonify(categorias_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}),