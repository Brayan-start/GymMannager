from app import db

class TipoMembresia(db.Model):
    __tablename__ = 'tipos_membresia'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    duracion_dias = db.Column(db.Integer, nullable=False)
    descripcion = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)

    membresias = db.relationship('Membresia', backref='tipo', lazy='dynamic')
    pagos = db.relationship('Pago', backref='tipo_membresia', lazy='dynamic')

    def __repr__(self):
        return f'<TipoMembresia {self.nombre}>'
