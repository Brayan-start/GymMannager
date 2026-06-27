from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import db
from app.models.asistencia import Asistencia
from app.models.clase import Clase
from app.models.miembro import Miembro
from app.routes import admin_required, instructor_required
from app.utils import bolivia_now, bolivia_date, bolivia_time, hoy_dia_semana
from app.models.horario import Horario
from datetime import datetime, date

asistencia_bp = Blueprint('asistencia', __name__)

@asistencia_bp.route('/')
@login_required
@instructor_required
def listar():
    fecha_str = request.args.get('fecha', bolivia_date().isoformat())
    try:
        fecha = date.fromisoformat(fecha_str)
    except:
        fecha = bolivia_date()
    clase_id = request.args.get('clase_id', '')
    query = Asistencia.query.filter(db.func.date(Asistencia.fecha) == fecha)
    if clase_id:
        query = query.filter_by(clase_id=clase_id)
    asistencias = query.order_by(Asistencia.hora_checkin.desc()).all()
    hoy_label = hoy_dia_semana()
    clases_hoy_ids = [h.clase_id for h in Horario.query.filter_by(dia_semana=hoy_label).all()]
    clases = Clase.query.filter(Clase.id.in_(clases_hoy_ids), Clase.activa == True).all() if clases_hoy_ids else []
    clase = Clase.query.get(int(clase_id)) if clase_id else None
    return render_template('asistencia/list.html', asistencias=asistencias, clases=clases, fecha=fecha, clase_id=clase_id, clase=clase, hoy_label=hoy_label)

@asistencia_bp.route('/checkin-directo', methods=['GET', 'POST'])
@login_required
@instructor_required
def checkin_directo():
    if request.method == 'POST':
        miembro_id = request.form.get('miembro_id')
        hoy = bolivia_date()
        exists = Asistencia.query.filter_by(
            miembro_id=miembro_id, fecha=hoy
        ).first()
        if not exists:
            asistencia = Asistencia(
                miembro_id=miembro_id,
                fecha=hoy,
                hora_checkin=bolivia_time(),
                asistio=True
            )
            db.session.add(asistencia)
            db.session.commit()
            flash('Check-in registrado', 'success')
        else:
            flash('El miembro ya tiene check-in hoy', 'warning')
        return redirect(url_for('asistencia.checkin_directo'))
    miembros = Miembro.query.filter_by(estado='activo').all()
    hoy = bolivia_date()
    asistencias_hoy = Asistencia.query.filter(
        db.func.date(Asistencia.fecha) == hoy
    ).order_by(Asistencia.hora_checkin.desc()).all()
    return render_template('asistencia/checkin_directo.html', miembros=miembros, asistencias=asistencias_hoy)

@asistencia_bp.route('/reporte')
@login_required
@admin_required
def reporte():
    desde = request.args.get('desde', bolivia_date().isoformat())
    hasta = request.args.get('hasta', bolivia_date().isoformat())
    try:
        d = date.fromisoformat(desde)
        h = date.fromisoformat(hasta)
    except:
        d = h = bolivia_date()
    asistencias = Asistencia.query.filter(
        db.func.date(Asistencia.fecha) >= d,
        db.func.date(Asistencia.fecha) <= h
    ).order_by(Asistencia.fecha.desc()).all()
    total = len(asistencias)
    miembros_unicos = len(set(a.miembro_id for a in asistencias))
    return render_template('asistencia/reporte.html', asistencias=asistencias, total=total, miembros_unicos=miembros_unicos, desde=d, hasta=h)
