from . import db
from ..utils import generate_uuid

# Modelo Tecnica
class Tecnica(db.Model):
    __tablename__ = 'tecnica'

    id_tecnica = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    duracion_estimada = db.Column(db.Integer, nullable=True)
    categoria = db.Column(db.String(50), nullable=True)  

    sesiones = db.relationship('Sesion', backref='tecnica_sesion', lazy=True)

    def to_dict(self):
        return {
            'id_tecnica': self.id_tecnica,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'duracion_estimada': self.duracion_estimada,
            'categoria': self.categoria
        }
