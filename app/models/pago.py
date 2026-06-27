from app import db
from datetime import datetime

METODOS_PAGO = [
    ('efectivo', 'Efectivo'),
    ('qr', 'QR'),
]

ESTADOS_PAGO = [
    ('pagado', 'Pagado'),
    ('pendiente', 'Pendiente'),
    ('rechazado', 'Rechazado'),
]

class Pago(db.Model):
    __tablename__ = 'pagos'

    id = db.Column(db.Integer, primary_key=True)
    miembro_id = db.Column(db.Integer, db.ForeignKey('miembros.id'), nullable=False)
    membresia_id = db.Column(db.Integer, db.ForeignKey('membresias.id'), nullable=True)
    tipo_membresia_id = db.Column(db.Integer, db.ForeignKey('tipos_membresia.id'), nullable=True)
    monto = db.Column(db.Float, nullable=False)
    fecha_pago = db.Column(db.DateTime, default=datetime.utcnow)
    metodo_pago = db.Column(db.String(20), default='efectivo')
    estado = db.Column(db.String(20), default='pagado')
    referencia = db.Column(db.String(100))
    comprobante_url = db.Column(db.String(255))
    motivo_rechazo = db.Column(db.Text)
    fecha_verificacion = db.Column(db.DateTime)
    verificado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)

    def __repr__(self):
        return f'<Pago ${self.monto} - {self.estado}>'
