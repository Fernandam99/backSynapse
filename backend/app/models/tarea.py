from datetime import datetime
from . import db
from app.models.usuario import Usuario
from app.models.sala import Sala
from ..utils import generate_uuid

# Modelo Tarea
class Tarea(db.Model):
    __tablename__ = 'tarea'

    id_tarea = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    usuario_id = db.Column(db.String(36), db.ForeignKey('usuario.id_usuario'), nullable=False)
    sala_id = db.Column(db.String(36), db.ForeignKey('sala.id_sala'), nullable=True)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    fecha_creacion = db.Column(db.DateTime(6), default=datetime.utcnow, nullable=False)
    completada = db.Column(db.Boolean, default=False)
    estado = db.Column(db.String(20), nullable=False)
    fecha_vencimiento = db.Column(db.Date, nullable=True)
    prioridad = db.Column(db.String(20), default='baja', nullable=False)
    comentario = db.Column(db.Text, nullable=True)

    sala = db.relationship('Sala', backref='tareas', lazy=True)

    def to_dict(self):
        return {
            'id_tarea': self.id_tarea,
            'usuario_id': self.usuario_id,
            'titulo': self.titulo,
            'descripcion': self.descripcion,
            'fecha_creacion': self.fecha_creacion.isoformat(),
            'completada': self.completada,
            'estado': self.estado,
            'fecha_vencimiento': self.fecha_vencimiento.isoformat() if self.fecha_vencimiento else None,
            'prioridad': self.prioridad,
            'comentario': self.comentario,
            'sala_id': self.sala_id
        }
