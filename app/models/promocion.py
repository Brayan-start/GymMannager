from app import db
from datetime import datetime

TIPOS_PROMO = [
    ('2x1', '2x1 (duplica duración)'),
    ('descuento_porcentaje', 'Descuento %'),
    ('descuento_monto', 'Descuento fijo (Bs.)'),
]

class Promocion(db.Model):
    __tablename__ = 'promociones'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.String(30), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    tipo_membresia_id = db.Column(db.Integer, db.ForeignKey('tipos_membresia.id'), nullable=True)
    fecha_inicio = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_fin = db.Column(db.DateTime, nullable=True)
    activo = db.Column(db.Boolean, default=True)
    descripcion = db.Column(db.Text)

    tipo_membresia = db.relationship('TipoMembresia', backref='promociones')

    @property
    def esta_activa(self):
        now = datetime.utcnow()
        if not self.activo:
            return False
        if self.fecha_inicio and self.fecha_inicio > now:
            return False
        if self.fecha_fin and self.fecha_fin < now:
            return False
        return True

    def calcular_precio_final(self, precio_original, duracion_dias):
        if self.tipo == '2x1':
            return precio_original, duracion_dias * 2
        elif self.tipo == 'descuento_porcentaje':
            desc = precio_original * (self.valor / 100)
            return precio_original - desc, duracion_dias
        elif self.tipo == 'descuento_monto':
            return max(precio_original - self.valor, 0), duracion_dias
        return precio_original, duracion_dias

    def __repr__(self):
        return f'<Promocion {self.nombre}>'
