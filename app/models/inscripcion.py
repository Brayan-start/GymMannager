from app import db
from datetime import datetime

class InscripcionClase(db.Model):
    __tablename__ = 'inscripciones_clase'

    id = db.Column(db.Integer, primary_key=True)
    miembro_id = db.Column(db.Integer, db.ForeignKey('miembros.id'), nullable=False)
    clase_id = db.Column(db.Integer, db.ForeignKey('clases.id'), nullable=False)
    fecha_inscripcion = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('miembro_id', 'clase_id', name='uq_miembro_clase'),)

    def __repr__(self):
        return f'<Inscripcion miembro={self.miembro_id} clase={self.clase_id}>'
