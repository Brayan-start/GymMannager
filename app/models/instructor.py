from app import db
from app.utils import bolivia_date
from datetime import datetime

class Instructor(db.Model):
    __tablename__ = 'instructores'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), unique=True, nullable=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(120))
    especialidad = db.Column(db.String(200))
    tarifa_por_clase = db.Column(db.Float, default=50.0)
    fecha_contratacion = db.Column(db.Date, default=bolivia_date)
    activo = db.Column(db.Boolean, default=True)

    clases = db.relationship('Clase', backref='instructor', lazy='dynamic')
    asistencias = db.relationship('AsistenciaInstructor', backref='instructor', lazy='dynamic', order_by='AsistenciaInstructor.fecha.desc()')

    @property
    def nombre_completo(self):
        return f'{self.nombre} {self.apellido}'

    def __repr__(self):
        return f'<Instructor {self.nombre} {self.apellido}>'
