from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, Sala, UsuarioSala, Usuario
import secrets
import string

sala_bp = Blueprint('sala', __name__)

def generate_access_code():
    """Generar código de acceso aleatorio para salas privadas"""
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
@sala_bp.route('', methods=['GET'])
@jwt_required()
def get_salas():
    try:
        usuario_id = get_jwt_identity()  # Obtener el ID del usuario actual
        
        # Obtener todas las salas donde el usuario está participando activamente
        salas_usuario = db.session.query(Sala).join(UsuarioSala).filter(
            UsuarioSala.id_usuario == usuario_id,  # Usar id_usuario
            UsuarioSala.activo == True  # Filtrar por usuarios activos
        ).all()

        # Devolver las salas como respuesta
        return jsonify([sala.to_dict() for sala in salas_usuario]), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@sala_bp.route('/publicas', methods=['GET'])
@jwt_required()
def get_salas_publicas():
    try:
        salas = Sala.query.filter_by(es_privada=False).all()
        return jsonify([sala.to_dict() for sala in salas]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sala_bp.route('/<string:sala_id>', methods=['GET'])
@jwt_required()
def get_sala(sala_id):
    try:
        # Obtener el usuario actual
        usuario_id = get_jwt_identity()

        # Verificar si el usuario está en la sala
        usuario_sala = UsuarioSala.query.filter_by(
            id_usuario=usuario_id,  # Cambiado de usuario_id a id_usuario
            id_sala=sala_id,
            activo=True
        ).first()

        if not usuario_sala:
            return jsonify({'error': 'No tienes acceso a esta sala'}), 403

        # Obtener la sala
        sala = Sala.query.get(sala_id)
        if not sala:
            return jsonify({'error': 'Sala no encontrada'}), 404

        # Incluir información de participantes
        sala_dict = sala.to_dict()
        participantes = db.session.query(Usuario).join(UsuarioSala).filter(
            UsuarioSala.id_sala == sala_id,
            UsuarioSala.activo == True
        ).all()

        sala_dict['participantes'] = [p.to_dict() for p in participantes]
        sala_dict['total_participantes'] = len(participantes)

        return jsonify(sala_dict), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sala_bp.route('', methods=['POST'])
@jwt_required()
def create_sala():
    try:
        # Obtener el ID del usuario autenticado
        usuario_id = get_jwt_identity()
        
        data = request.get_json()
        
        # Validar datos requeridos
        if not data.get('nombre'):
            return jsonify({'error': 'El nombre de la sala es requerido'}), 400
        
        # Generar código de acceso si es privada
        codigo_acceso = None
        if data.get('es_privada', False):
            codigo_acceso = generate_access_code()
        
        # Crear nueva sala
        nueva_sala = Sala(
            nombre=data['nombre'],
            descripcion=data.get('descripcion'),
            max_participantes=data.get('max_participantes'),
            es_privada=data.get('es_privada', False),
            creador_id=usuario_id,  # Asignamos el creador_id al usuario autenticado
            codigo_acceso=codigo_acceso
        )
        
        db.session.add(nueva_sala)
        db.session.flush()  # Para obtener el ID de la sala
        
        # Agregar al creador como líder de la sala
        usuario_sala = UsuarioSala(
            id_usuario=usuario_id,  # Cambio aquí a 'id_usuario'
            id_sala=nueva_sala.id_sala,
            rol_en_sala='lider'
        )
        
        db.session.add(usuario_sala)
        db.session.commit()
        
        return jsonify(nueva_sala.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
@sala_bp.route('/<string:sala_id>/actualizar', methods=['PUT'])
@jwt_required()
def actualizar_usuario_sala(sala_id):
    try:
        # Obtener el usuario actual
        usuario_id = get_jwt_identity()
        data = request.get_json()

        # Buscar si el usuario está en la sala especificada
        usuario_sala = UsuarioSala.query.filter_by(
            id_usuario=usuario_id, 
            id_sala=sala_id
        ).first()

        if not usuario_sala:
            return jsonify({'error': 'Usuario no encontrado en esta sala'}), 404

        # Actualizar datos del usuario en la sala (ejemplo: cambiar el rol)
        if 'rol_en_sala' in data:
            usuario_sala.rol_en_sala = data['rol_en_sala']
        
        if 'activo' in data:
            usuario_sala.activo = data['activo']

        # Guardar cambios
        db.session.commit()

        return jsonify({'message': 'Usuario en sala actualizado correctamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@sala_bp.route('/<string:sala_id>', methods=['DELETE'])
@jwt_required()
def delete_sala(sala_id):
    try:
        # Obtener el usuario actual desde el JWT
        usuario_id = get_jwt_identity()
        
        # Verificar que el usuario es líder de la sala
        usuario_sala = UsuarioSala.query.filter_by(
            id_usuario=usuario_id,  # Revisar si "usuario_id" está bien definido en el modelo
            id_sala=sala_id,
            rol_en_sala='lider',
            activo=True
        ).first()

        # Si el usuario no es líder o no está en la sala
        if not usuario_sala:
            return jsonify({'error': 'No tienes permisos para eliminar esta sala'}), 403

        # Buscar la sala
        sala = Sala.query.get(sala_id)
        if not sala:
            return jsonify({'error': 'Sala no encontrada'}), 404

        # Desactivar todos los usuarios de la sala
        UsuarioSala.query.filter_by(sala_id=sala_id).update({'activo': False})
        
        # Eliminar la sala
        db.session.delete(sala)
        db.session.commit()

        return jsonify({'message': 'Sala eliminada exitosamente'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@sala_bp.route('/unirse', methods=['POST'])
@jwt_required()
def unirse_sala():
    try:
        usuario_id = get_jwt_identity()  # Obtener ID del usuario del JWT
        data = request.get_json()
        
        sala_id = data.get('sala_id')
        codigo_acceso = data.get('codigo_acceso')
        
        if not sala_id:
            return jsonify({'error': 'ID de sala es requerido'}), 400
        
        # Buscar la sala en la base de datos
        sala = Sala.query.get(sala_id)
        if not sala:
            return jsonify({'error': 'Sala no encontrada'}), 404
        
        # Verificar código de acceso para salas privadas
        if sala.es_privada and sala.codigo_acceso != codigo_acceso:
            return jsonify({'error': 'Código de acceso incorrecto'}), 403
        
        # Verificar si el usuario ya está en la sala
        usuario_sala_existente = UsuarioSala.query.filter_by(
            id_usuario=usuario_id,  # Aquí se usa "id_usuario" y no "usuario_id" en el filtro
            id_sala=sala_id
        ).first()
        
        if usuario_sala_existente:
            if usuario_sala_existente.activo:
                return jsonify({'error': 'Ya eres miembro de esta sala'}), 400
            else:
                # Si está inactivo, lo reactivamos
                usuario_sala_existente.activo = True
        else:
            # Verificar el límite de participantes
            if sala.max_participantes:
                participantes_activos = UsuarioSala.query.filter_by(
                    id_sala=sala_id,
                    activo=True
                ).count()
                
                if participantes_activos >= sala.max_participantes:
                    return jsonify({'error': 'La sala ha alcanzado el límite de participantes'}), 400
            
            # Crear nueva membresía
            usuario_sala_nueva = UsuarioSala(
                id_usuario=usuario_id,  # Asegúrate de usar "id_usuario"
                id_sala=sala_id,
                rol_en_sala='invitado',  # El rol de nuevo miembro
                activo=True  # Establecer al usuario como activo por defecto
            )
            db.session.add(usuario_sala_nueva)
        
        # Guardar cambios
        db.session.commit()
        
        return jsonify({'message': 'Te has unido a la sala exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@sala_bp.route('/<string:sala_id>/salir', methods=['POST'])
@jwt_required()
def salir_sala(sala_id):
    try:
        usuario_id = get_jwt_identity()
        
        # Verificar si el usuario está en la sala y si está activo
        usuario_sala = UsuarioSala.query.filter_by(
            id_usuario=usuario_id,
            id_sala=sala_id,
            activo=True
        ).first()
        
        if not usuario_sala:
            return jsonify({'error': 'No eres miembro activo de esta sala'}), 400
        
        # Si el usuario es líder, asegurarse de que no se quede sin líder
        if usuario_sala.rol_en_sala == 'lider':
            otros_lideres = UsuarioSala.query.filter_by(
                id_sala=sala_id,
                rol_en_sala='lider',
                activo=True
            ).filter(UsuarioSala.id_usuario != usuario_id).count()
            
            if otros_lideres == 0:
                # Si no hay más líderes, transferir liderazgo al primer invitado activo
                nuevo_lider = UsuarioSala.query.filter_by(
                    id_sala=sala_id,
                    rol_en_sala='invitado',
                    activo=True
                ).first()
                
                if nuevo_lider:
                    nuevo_lider.rol_en_sala = 'lider'
                else:
                    # Si no hay más participantes activos, podrías decidir eliminar la sala o mantenerla sin líder.
                    # Pero por ahora vamos a dejarla sin líder.
                    pass
        
        # Desactivar la membresía del usuario en la sala
        usuario_sala.activo = False
        db.session.commit()
        
        return jsonify({'message': 'Has salido de la sala exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
