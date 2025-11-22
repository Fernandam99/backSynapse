from . import db
from ..utils import generate_uuid

# Modelo SesionTecnicaParam
class SesionTecnicaParam(db.Model):
    __tablename__ = 'sesiontecnicaparam'

    id_param = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    id_sesion = db.Column(db.String(36), db.ForeignKey('sesion.id_sesion'), nullable=False)
    parametro = db.Column(db.String(100), nullable=False)
    valor = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            'id_param': self.id_param,
            'id_sesion': self.id_sesion,
            'parametro': self.parametro,
            'valor': self.valor
        }
