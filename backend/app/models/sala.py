from datetime import datetime
from . import db
from app.models.usuario import Usuario
from ..utils import generate_uuid

# Modelo Sala
class Sala(db.Model):
    __tablename__ = 'sala'

    id_sala = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    fecha_creacion = db.Column(db.DateTime(6), default=datetime.utcnow, nullable=False)
    creador_id = db.Column(db.String(36), db.ForeignKey('usuario.id_usuario'), nullable=False)
    max_participantes = db.Column(db.Integer, nullable=True)
    es_privada = db.Column(db.Boolean, default=False)
    codigo_acceso = db.Column(db.String(6), nullable=True)
    estado = db.Column(db.String(20), default='activa', nullable=False)

    # Relaciones
    usuarios_sala = db.relationship('UsuarioSala', back_populates='sala', lazy=True)
    sesiones_sala = db.relationship('SalaSesion', backref='sala_sesion_rel', lazy=True)


    def to_dict(self):
        return {
            'id_sala': self.id_sala,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'creador_id': self.creador_id,
            'max_participantes': self.max_participantes,
            'es_privada': self.es_privada,
            'codigo_acceso': self.codigo_acceso,
            'estado': self.estado
        }
