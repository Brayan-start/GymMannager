from app import db
from app.utils import bolivia_date, bolivia_time

class AsistenciaInstructor(db.Model):
    __tablename__ = 'asistencia_instructor'

    id = db.Column(db.Integer, primary_key=True)
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructores.id'), nullable=False)
    clase_id = db.Column(db.Integer, db.ForeignKey('clases.id'), nullable=True)
    fecha = db.Column(db.Date, default=bolivia_date, nullable=False)
    hora_entrada = db.Column(db.Time, default=bolivia_time)
    hora_salida = db.Column(db.Time)
    estado = db.Column(db.String(20), default='presente')
    observacion = db.Column(db.Text)
    pago_realizado = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<AsistenciaInstructor {self.id} - {self.fecha}>'
