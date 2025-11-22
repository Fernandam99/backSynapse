from datetime import datetime
from . import db
from app.models.usuario import Usuario
from app.models.tecnica import Tecnica
from ..utils import generate_uuid

# Modelo Sesion
class Sesion(db.Model):
    __tablename__ = 'sesion'

    id_sesion = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    usuario_id = db.Column(db.String(36), db.ForeignKey('usuario.id_usuario'), nullable=False)
    tecnica_id = db.Column(db.String(36), db.ForeignKey('tecnica.id_tecnica'), nullable=False)
    fecha_inicio = db.Column(db.DateTime(6), default=datetime.utcnow, nullable=False)
    fecha_fin = db.Column(db.DateTime(6), nullable=True)
    duracion_real = db.Column(db.Integer, nullable=True) 
    estado = db.Column(db.String(20), nullable=False)
    es_grupal = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id_sesion': self.id_sesion,
            'usuario_id': self.usuario_id,
            'tecnica_id': self.tecnica_id,
            'fecha_inicio': self.fecha_inicio.isoformat(),
            'fecha_fin': self.fecha_fin.isoformat() if self.fecha_fin else None,
            'completada': self.estado == 'Completado',  
            'duracion_real': self.duracion_real,
            'estado': self.estado,
            'es_grupal': self.es_grupal
        }