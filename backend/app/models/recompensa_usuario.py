from datetime import datetime
from . import db

# Modelo RecompensaUsuario
class RecompensaUsuario(db.Model):
    __tablename__ = 'recompensausuario'

    id_usuario = db.Column(db.String(36), db.ForeignKey('usuario.id_usuario'), primary_key=True)
    id_recompensa = db.Column(db.String(36), db.ForeignKey('recompensa.id_recompensa'), primary_key=True)
    fecha_obtenida = db.Column(db.DateTime(6), default=datetime.utcnow, nullable=False)
    consumida = db.Column(db.Boolean, default=False, nullable=False)

    def to_dict(self):
        return {
            'id_usuario': self.id_usuario,
            'id_recompensa': self.id_recompensa,
            'fecha_obtenida': self.fecha_obtenida.isoformat(),
            'consumida': self.consumida
        }
