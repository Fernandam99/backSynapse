# backend/app/models/usuario.py
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from . import db
from app.models.rol import Rol
import uuid

def generate_uuid():
    return str(uuid.uuid4())

# Modelo Usuario
class Usuario(db.Model):
    __tablename__ = 'usuario'

    id_usuario = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    username = db.Column(db.String(100), unique=True, nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    celular = db.Column(db.String(15), nullable=True) # Existe, pero puede renombrarse a telefono
    avatar_url = db.Column(db.String(255), nullable=True) # Existe
    fecha_registro = db.Column(db.DateTime(6), default=datetime.utcnow, nullable=False)
    ultimo_acceso = db.Column(db.DateTime(6), nullable=True)
    rol_id = db.Column(db.Integer, db.ForeignKey('rol.id'), nullable=False)
    activo = db.Column(db.Boolean, default=True, nullable=False)

    # --- Nuevos campos para el perfil ---
    nombre_completo = db.Column(db.String(200), nullable=True) # Añadido
    telefono = db.Column(db.String(20), nullable=True)         # Renombrar de 'celular' o usar este nuevo
    ubicacion = db.Column(db.String(200), nullable=True)      # Añadido
    fecha_nacimiento = db.Column(db.Date, nullable=True)       # Añadido
    descripcion = db.Column(db.Text, nullable=True)            # Añadido
    # ----------------------------

    # Relaciones
    tareas = db.relationship('Tarea', backref='usuario_tarea', lazy=True)
    sesiones = db.relationship('Sesion', backref='usuario_sesion', lazy=True)
    salas = db.relationship('UsuarioSala', backref='usuario_sala', lazy=True)
    recompensas = db.relationship('RecompensaUsuario', backref='usuario_recompensa', lazy=True)
    progreso = db.relationship('Progreso', backref='usuario_progreso', lazy=True)

    def to_dict(self):
            return {
                'id_usuario': self.id_usuario,
                'username': self.username,
                'correo': self.correo,
                'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None,
                'ultimo_acceso': self.ultimo_acceso.isoformat() if self.ultimo_acceso else None,
                'rol_id': self.rol_id,
                'activo': self.activo,
                # --- Incluir nuevos campos ---
                'nombre_completo': self.nombre_completo,
                'telefono': self.telefono,
                'ubicacion': self.ubicacion,
                'fecha_nacimiento': self.fecha_nacimiento.isoformat() if self.fecha_nacimiento else None,
                'descripcion': self.descripcion,
                'avatar_url': self.avatar_url
                # ----------------------------
            }