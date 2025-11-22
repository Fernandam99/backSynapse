from . import db
from ..utils import generate_uuid

# Modelo Recompensa
class Recompensa(db.Model):
    __tablename__ = 'recompensa'

    id_recompensa = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    puntos_requeridos = db.Column(db.Integer, nullable=True)
    tipo = db.Column(db.String(50), nullable=False)
    valor = db.Column(db.Integer, nullable=False)
    requisitos = db.Column(db.JSON, nullable=False)

    usuarios_recompensa = db.relationship('RecompensaUsuario', backref='recompensa', lazy=True)

    def to_dict(self):
        return {
            'id_recompensa': self.id_recompensa,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'puntos_requeridos': self.puntos_requeridos,
            'tipo': self.tipo,
            'valor': self.valor,
            'requisitos': self.requisitos
        }
