from datetime import date
from . import db
from ..utils import generate_uuid
# Modelo Progreso
class Progreso(db.Model):
    __tablename__ = 'progreso'

    id_progreso = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    usuario_id = db.Column(db.String(36), db.ForeignKey('usuario.id_usuario'), nullable=False)
    fecha = db.Column(db.Date, default=date.today, nullable=False)
    tareas_completadas = db.Column(db.Integer, default=0, nullable=False)
    sesiones_completadas = db.Column(db.Integer, default=0, nullable=False)
    puntos_acumulados = db.Column(db.Integer, default=0, nullable=False)
    minutos_estudio = db.Column(db.Integer, default=0, nullable=False)
    sesiones_realizadas = db.Column(db.Integer, default=0, nullable=False)

    def to_dict(self):
        return {
            'id_progreso': self.id_progreso,
            'usuario_id': self.usuario_id,
            'fecha': self.fecha.isoformat(),
            'tareas_completadas': self.tareas_completadas,
            'sesiones_completadas': self.sesiones_completadas,
            'puntos_acumulados': self.puntos_acumulados,
            'minutos_estudio': self.minutos_estudio,
            'sesiones_realizadas': self.sesiones_realizadas
        }
