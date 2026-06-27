from app import db
from datetime import datetime

class Miembro(db.Model):
    __tablename__ = 'miembros'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), unique=True, nullable=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    ci = db.Column(db.String(20))
    email = db.Column(db.String(120))
    telefono = db.Column(db.String(20))
    direccion = db.Column(db.Text)
    fecha_nacimiento = db.Column(db.Date)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(20), default='activo')
    foto_url = db.Column(db.String(255))

    membresias = db.relationship('Membresia', backref='miembro', lazy='dynamic', order_by='Membresia.fecha_inicio.desc()')
    pagos = db.relationship('Pago', backref='miembro', lazy='dynamic', order_by='Pago.fecha_pago.desc()')
    asistencias = db.relationship('Asistencia', backref='miembro', lazy='dynamic')

    @property
    def nombre_completo(self):
        return f'{self.nombre} {self.apellido}'

    @property
    def membresia_activa(self):
        from datetime import datetime
        from app.models.membresia import Membresia
        return self.membresias.filter_by(estado='activa').filter(
            Membresia.fecha_fin >= datetime.utcnow()
        ).first()

    def __repr__(self):
        return f'<Miembro {self.nombre} {self.apellido}>'
