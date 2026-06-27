from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app import db
from app.models.clase import Clase
from app.models.asistencia import Asistencia
from app.models.miembro import Miembro
from app.models.instructor import Instructor
from app.models.horario import Horario
from app.models.asistencia_instructor import AsistenciaInstructor
from app.routes import instructor_required
from app.utils import bolivia_now, bolivia_date, hoy_dia_semana
from datetime import datetime, date, timedelta
from sqlalchemy import func

instructor_bp = Blueprint('instructor', __name__)

@instructor_bp.route('/dashboard')
@login_required
@instructor_required
def dashboard():
    hoy = bolivia_date()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    hoy_label = hoy_dia_semana()

    clases_hoy_ids = [h.clase_id for h in Horario.query.filter_by(dia_semana=hoy_label).all()]
    clases_hoy = Clase.query.filter(Clase.id.in_(clases_hoy_ids), Clase.activa == True).all() if clases_hoy_ids else []
    total_clases = len(clases_hoy)

    asistencias_hoy = Asistencia.query.filter(
        func.date(Asistencia.fecha) == hoy
    ).count()

    asistencias_semana = Asistencia.query.filter(
        func.date(Asistencia.fecha) >= inicio_semana
    ).count()

    miembros_activos = Miembro.query.filter_by(estado='activo').count()

    asistencias_por_clase = db.session.query(
        Clase.nombre, func.count(Asistencia.id).label('total')
    ).join(Asistencia, Asistencia.clase_id == Clase.id
    ).filter(func.date(Asistencia.fecha) >= inicio_semana
    ).group_by(Clase.id, Clase.nombre
    ).order_by(func.count(Asistencia.id).desc()).all()

    return render_template('instructor/dashboard.html',
        now=bolivia_now(),
        hoy_label=hoy_label,
        total_clases=total_clases,
        asistencias_hoy=asistencias_hoy,
        asistencias_semana=asistencias_semana,
        miembros_activos=miembros_activos,
        clases=clases_hoy,
        asistencias_por_clase=asistencias_por_clase
    )

@instructor_bp.route('/asistencia')
@login_required
@instructor_required
def asistencia():
    instr = Instructor.query.filter_by(usuario_id=current_user.id).first()
    hoy = bolivia_date()
    hoy_label = hoy_dia_semana()
    clases_hoy_ids = [h.clase_id for h in Horario.query.filter_by(dia_semana=hoy_label).all()]
    clases = Clase.query.filter(Clase.id.in_(clases_hoy_ids), Clase.activa == True).all() if clases_hoy_ids else []
    asistencias = Asistencia.query.filter(
        func.date(Asistencia.fecha) == hoy
    ).order_by(Asistencia.hora_checkin.desc()).all()
    mi_asistencia = AsistenciaInstructor.query.filter_by(
        instructor_id=instr.id if instr else 0
    ).order_by(AsistenciaInstructor.fecha.desc()).limit(20).all()
    return render_template('instructor/asistencia.html',
        clases=clases, asistencias=asistencias, fecha=hoy,
        mi_asistencia=mi_asistencia, now=bolivia_now())

@instructor_bp.route('/clases')
@login_required
@instructor_required
def clases():
    hoy = bolivia_date()
    hoy_label = hoy_dia_semana()
    clases_hoy_ids = [h.clase_id for h in Horario.query.filter_by(dia_semana=hoy_label).all()]
    clases = Clase.query.filter(Clase.id.in_(clases_hoy_ids), Clase.activa == True).all() if clases_hoy_ids else []
    return render_template('instructor/clases.html', clases=clases, hoy_label=hoy_label)

@instructor_bp.route('/horario')
@login_required
@instructor_required
def horario():
    hoy = bolivia_date()
    hoy_label = hoy_dia_semana()
    horarios = Horario.query.join(Clase).filter(Clase.activa == True).order_by(Horario.dia_semana, Horario.hora_inicio).all()
    return render_template('instructor/horario.html', horarios=horarios, hoy_label=hoy_label, now=bolivia_now())
