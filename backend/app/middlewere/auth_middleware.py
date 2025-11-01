from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from flask import jsonify
from backend.models import Usuario, Rol

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        usuario_id = get_jwt_identity()
        usuario = Usuario.query.get(usuario_id)
        if not usuario or not usuario.rol or usuario.rol.nombre != 'admin':
            return jsonify({'error': 'Acceso denegado. Se requieren permisos de administrador.'}), 403
        return f(*args, **kwargs)
    return decorated_function

def active_user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        usuario_id = get_jwt_identity()
        usuario = Usuario.query.get(usuario_id)
        if not usuario or not usuario.activo:
            return jsonify({'error': 'Usuario inactivo o no encontrado.'}), 401
        return f(*args, **kwargs)
    return decorated_function
