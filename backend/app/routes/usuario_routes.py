from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, Usuario, Rol
from werkzeug.security import generate_password_hash

usuario_bp = Blueprint('usuario', __name__)

@usuario_bp.route('', methods=['GET'])
@jwt_required()
def get_usuarios():
    try:
        usuarios = Usuario.query.all()
        return jsonify([usuario.to_dict() for usuario in usuarios]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@usuario_bp.route('/<string:usuario_id>', methods=['GET'])
@jwt_required()
def get_usuario(usuario_id):
    try:
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        return jsonify(usuario.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@usuario_bp.route('', methods=['POST'])
@jwt_required()
def create_usuario():
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        if not data.get('correo') or not data.get('password'):
            return jsonify({'error': 'Email y contraseña son requeridos'}), 400
        
        # Verificar si el usuario ya existe
        if Usuario.query.filter_by(correo=data['correo']).first():
            return jsonify({'error': 'El email ya está registrado'}), 400
        
        # Validar rol_id
        rol_id = data.get('rol_id', 2)  # Por defecto usuario
        if not Rol.query.get(rol_id):
            return jsonify({'error': 'Rol no válido'}), 400
        
        # Crear nuevo usuario
        nuevo_usuario = Usuario(
            Username=data.get('Username'),
            correo=data['correo'],
            password=generate_password_hash(data['password']),
            rol_id=rol_id,
            activo=data.get('activo', True)
        )
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        return jsonify(nuevo_usuario.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@usuario_bp.route('/<string:usuario_id>', methods=['PUT'])
@jwt_required()
def update_usuario(usuario_id):
    try:
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        data = request.get_json()
        
        # Actualizar campos permitidos
        if 'Username' in data:
            usuario.Username = data['Username']
        
        if 'correo' in data:
            # Verificar que el nuevo email no esté en uso por otro usuario
            existing_user = Usuario.query.filter_by(correo=data['correo']).first()
            if existing_user and existing_user.id_usuario != usuario_id:
                return jsonify({'error': 'El email ya está en uso'}), 400
            usuario.correo = data['correo']
        
        if 'rol_id' in data:
            if not Rol.query.get(data['rol_id']):
                return jsonify({'error': 'Rol no válido'}), 400
            usuario.rol_id = data['rol_id']
        
        if 'activo' in data:
            usuario.activo = data['activo']
        
        if 'password' in data and data['password']:
            usuario.password = generate_password_hash(data['password'])
        
        db.session.commit()
        
        return jsonify(usuario.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@usuario_bp.route('/<string:usuario_id>', methods=['DELETE'])
@jwt_required()
def delete_usuario(usuario_id):
    try:
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # Desactivar en lugar de eliminar (soft delete)
        usuario.activo = False
        db.session.commit()
        
        return jsonify({'message': 'Usuario desactivado exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@usuario_bp.route('/search', methods=['GET'])
@jwt_required()
def search_usuarios():
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify([]), 200
        
        usuarios = Usuario.query.filter(
            db.or_(
                Usuario.Username.like(f'%{query}%'),
                Usuario.correo.like(f'%{query}%')
            )
        ).all()
        
        return jsonify([usuario.to_dict() for usuario in usuarios]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500