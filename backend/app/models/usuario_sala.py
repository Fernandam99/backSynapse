from datetime import datetime
from . import db
from app.models.usuario import Usuario
from app.models.sala import Sala

# Modelo UsuarioSala
class UsuarioSala(db.Model):
    __tablename__ = 'usuariosala'

    id_usuario = db.Column(db.String(36), db.ForeignKey('usuario.id_usuario'), primary_key=True)
    id_sala = db.Column(db.String(36), db.ForeignKey('sala.id_sala'), primary_key=True)
    fecha_union = db.Column(db.DateTime(6), default=datetime.utcnow, nullable=False)
    rol_en_sala = db.Column(db.String(50), nullable=False)
    activo = db.Column(db.Boolean, default=True)

    # Relación inversa para acceder a la sala
    sala = db.relationship('Sala', back_populates='usuarios_sala')

    def to_dict(self):
        return {
            'id_usuario': self.id_usuario,
            'id_sala': self.id_sala,
            'fecha_union': self.fecha_union.isoformat(),
            'rol_en_sala': self.rol_en_sala,
            'activo': self.activo
        }
