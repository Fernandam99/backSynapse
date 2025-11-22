from . import db

# Modelo SalaSesion
class SalaSesion(db.Model):
    __tablename__ = 'salasesion'

    id_sala = db.Column(db.String(36), db.ForeignKey('sala.id_sala'), primary_key=True)
    id_sesion = db.Column(db.String(36), db.ForeignKey('sesion.id_sesion'), primary_key=True)

    def to_dict(self):
        return {
            'id_sala': self.id_sala,
            'id_sesion': self.id_sesion
        }
