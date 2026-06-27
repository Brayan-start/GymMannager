from app import db
from datetime import datetime

class Membresia(db.Model):
    __tablename__ = 'membresias'

    id = db.Column(db.Integer, primary_key=True)
    miembro_id = db.Column(db.Integer, db.ForeignKey('miembros.id'), nullable=False)
    tipo_id = db.Column(db.Integer, db.ForeignKey('tipos_membresia.id'), nullable=False)
    fecha_inicio = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_fin = db.Column(db.DateTime, nullable=False)
    estado = db.Column(db.String(20), default='activa')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Membresia {self.id} - {self.estado}>'
