from app import db
from datetime import datetime

class Clase(db.Model):
    __tablename__ = 'clases'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    categoria = db.Column(db.String(100))
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructores.id'), nullable=True)
    cupo_maximo = db.Column(db.Integer, default=20)
    activa = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    horarios = db.relationship('Horario', backref='clase', lazy='dynamic', cascade='all, delete-orphan')
    asistencias = db.relationship('Asistencia', backref='clase', lazy='dynamic')
    inscripciones = db.relationship('InscripcionClase', backref='clase', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def asistentes_hoy(self):
        hoy = datetime.utcnow().date()
        return self.asistencias.filter(
            db.func.date(Asistencia.fecha) == hoy,
            Asistencia.asistio == True
        ).count()

    def __repr__(self):
        return f'<Clase {self.nombre}>'

from app.models.asistencia import Asistencia
from app.models.inscripcion import InscripcionClase
