from app import db
from app.utils import bolivia_date, bolivia_time

class Asistencia(db.Model):
    __tablename__ = 'asistencia'

    id = db.Column(db.Integer, primary_key=True)
    miembro_id = db.Column(db.Integer, db.ForeignKey('miembros.id'), nullable=False)
    clase_id = db.Column(db.Integer, db.ForeignKey('clases.id'), nullable=True)
    fecha = db.Column(db.Date, default=bolivia_date, nullable=False)
    hora_checkin = db.Column(db.Time, default=bolivia_time)
    asistio = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Asistencia {self.id} - {self.fecha}>'
