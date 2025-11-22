# backend/app/routes/auth.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from ..models import db, Usuario, Rol
from ..utils.validators import validate_email, validate_password
from datetime import datetime
import os # Para manejar la subida de archivos (si aplica)
from werkzeug.utils import secure_filename

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()

        # Validar campos requeridos
        if not data.get('username') or not data.get('correo') or not data.get('password'):
            return jsonify({'error': 'Username, email y contraseña son requeridos'}), 400

        # Validar formato de email
        email_valid, email_msg = validate_email(data['correo'])
        if not email_valid:
            return jsonify({'error': email_msg}), 400

        # Validar fortaleza de contraseña
        password_valid, password_msg = validate_password(data['password'])
        if not password_valid:
            return jsonify({'error': password_msg}), 400

        # Verificar si el email ya existe
        if Usuario.query.filter_by(correo=data['correo']).first():
            return jsonify({'error': 'El email ya está registrado'}), 400

        # Verificar si el username ya existe
        if Usuario.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'El username ya está registrado'}), 400

        # Obtener rol por defecto (usuario)
        rol_usuario = Rol.query.filter_by(nombre='usuario').first()
        if not rol_usuario:
            return jsonify({'error': 'Rol de usuario no encontrado'}), 500

        # Crear nuevo usuario
        nuevo_usuario = Usuario(
            username=data['username'],
            correo=data['correo'],
            password=generate_password_hash(data['password']),
            rol_id=rol_usuario.id
        )

        db.session.add(nuevo_usuario)
        db.session.commit()

        return jsonify({
            'message': 'Usuario registrado exitosamente',
            'usuario': nuevo_usuario.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()

        # Validar datos requeridos
        if not data.get('correo') or not data.get('password'):
            return jsonify({'error': 'Email y contraseña son requeridos'}), 400

        # Buscar usuario
        usuario = Usuario.query.filter_by(correo=data['correo']).first()

        if not usuario or not check_password_hash(usuario.password, data['password']):
            return jsonify({'error': 'Credenciales inválidas'}), 401

        if not usuario.activo:
            return jsonify({'error': 'Cuenta desactivada'}), 401

        # Actualizar último acceso
        usuario.ultimo_acceso = datetime.utcnow()
        db.session.commit()

        # Crear token JWT
        access_token = create_access_token(identity=usuario.id_usuario)

        return jsonify({
            'access_token': access_token,
            'usuario': usuario.to_dict()
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        usuario_id = get_jwt_identity()
        usuario = Usuario.query.get(usuario_id)

        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        # El to_dict() ya incluye los nuevos campos si se agregaron al modelo
        return jsonify(usuario.to_dict()), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- Nuevo endpoint para actualizar perfil del usuario actual ---
@auth_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_current_user():
    try:
        usuario_id = get_jwt_identity()
        usuario = Usuario.query.get(usuario_id)

        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        # Manejar datos de formulario o JSON
        # request.form se usa para datos y archivos (multipart/form-data)
        # request.get_json() se usa para JSON puro
        # Flask lo maneja automáticamente en este contexto para acceder a ambos.
        data = request.form if request.form else request.get_json()

        # Actualizar campos permitidos
        if 'username' in data:
            new_username = data['username']
            # Verificar unicidad si se cambia
            if new_username != usuario.username and Usuario.query.filter_by(username=new_username).first():
                 return jsonify({'error': 'El username ya está registrado'}), 400
            usuario.username = new_username

        if 'correo' in data:
            new_correo = data['correo']
            # Verificar unicidad si se cambia
            if new_correo != usuario.correo and Usuario.query.filter_by(correo=new_correo).first():
                 return jsonify({'error': 'El email ya está registrado'}), 400
            usuario.correo = new_correo

        # --- Actualizaciones para campos de perfil ---
        if 'nombre_completo' in data:
            usuario.nombre_completo = data['nombre_completo']

        if 'telefono' in data:
            usuario.telefono = data['telefono']

        if 'ubicacion' in data:
            usuario.ubicacion = data['ubicacion']

        if 'fecha_nacimiento' in data and data['fecha_nacimiento']:
            try:
                # Asumiendo formato YYYY-MM-DD
                usuario.fecha_nacimiento = datetime.strptime(data['fecha_nacimiento'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Formato de fecha de nacimiento inválido (YYYY-MM-DD)'}), 400

        if 'descripcion' in data:
            usuario.descripcion = data['descripcion']

        # Manejo de avatar
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename != '':
                # --- Lógica de subida de archivo ---
                # Asegúrate de tener una carpeta 'uploads' o similar
                upload_folder = os.environ.get('UPLOAD_FOLDER', 'uploads') # Define UPLOAD_FOLDER en .env o config
                os.makedirs(upload_folder, exist_ok=True)
                filename = secure_filename(file.filename)
                file_path = os.path.join(upload_folder, f"{usuario.id_usuario}_{filename}")
                file.save(file_path)
                # Guardar ruta relativa o URL pública
                usuario.avatar_url = f"/uploads/{os.path.basename(file_path)}" # Ajusta según tu servidor de archivos

        # Opción para eliminar avatar
        if 'remove_avatar' in data and data.get('remove_avatar') == '1':
             # Opcional: Eliminar archivo físico si existe
             if usuario.avatar_url:
                 try:
                     file_path_to_delete = os.path.join('backend', usuario.avatar_url.lstrip('/')) # Ajusta la ruta
                     if os.path.exists(file_path_to_delete):
                         os.remove(file_path_to_delete)
                 except OSError:
                     pass # No hacer nada si no se puede eliminar el archivo
             usuario.avatar_url = None


        db.session.commit()

        # Devolver el usuario actualizado
        return jsonify(usuario.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        print(f"[ERROR UPDATE PROFILE] {str(e)}")
        return jsonify({'error': 'Error interno al actualizar el perfil'}), 500
# --- Fin del nuevo endpoint ---

@auth_bp.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    try:
        usuario_id = get_jwt_identity()
        data = request.get_json()

        if not data.get('current_password') or not data.get('new_password'):
            return jsonify({'error': 'Contraseña actual y nueva son requeridas'}), 400

        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        # Verificar contraseña actual
        if not check_password_hash(usuario.password, data['current_password']):
            return jsonify({'error': 'Contraseña actual incorrecta'}), 400

        # Actualizar contraseña
        usuario.password = generate_password_hash(data['new_password'])
        db.session.commit()

        return jsonify({'message': 'Contraseña actualizada exitosamente'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Opcional: Endpoint para eliminar la cuenta
@auth_bp.route('/delete-account', methods=['POST'])
@jwt_required()
def delete_account():
    try:
        usuario_id = get_jwt_identity()
        data = request.get_json()
        password = data.get('password')

        if not password:
            return jsonify({'error': 'Contraseña es requerida para eliminar la cuenta'}), 400

        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        if not check_password_hash(usuario.password, password):
            return jsonify({'error': 'Contraseña incorrecta'}), 400

        # Aquí podrías implementar una lógica de "soft delete" o eliminación real
        # Por ejemplo, desactivar al usuario:
        usuario.activo = False
        # O eliminarlo completamente (¡peligroso!):
        # db.session.delete(usuario)

        db.session.commit()
        # Opcional: revocar token (requiere manejo adicional)
        return jsonify({'message': 'Cuenta eliminada exitosamente'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Opcional: Endpoint para cerrar sesión en todos los dispositivos
# Esto generalmente implica manejar tokens revocados en una lista negra (blacklist)
# o usar una estrategia de refresh token.
# Por simplicidad, aquí solo se podría devolver un mensaje indicando
# que el cliente debe borrar su token localmente.
@auth_bp.route('/logout-all-devices', methods=['POST'])
@jwt_required()
def logout_all_devices():
    try:
        usuario_id = get_jwt_identity()
        data = request.get_json()
        password = data.get('password')

        if not password:
            return jsonify({'error': 'Contraseña es requerida para cerrar sesión en otros dispositivos'}), 400

        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        if not check_password_hash(usuario.password, password):
            return jsonify({'error': 'Contraseña incorrecta'}), 400

        # En una implementación real, aquí se añadiría el token a una blacklist
        # o se invalidaría el refresh token del usuario.
        # Por ahora, simplemente devolvemos un mensaje.
        return jsonify({'message': 'Por favor, cierre sesión en otros dispositivos borrando el token localmente.'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
