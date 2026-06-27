from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from app import db
from app.models.clase import Clase
from app.models.horario import Horario, DIAS_SEMANA
from app.models.instructor import Instructor
from app.models.asistencia import Asistencia
from app.models.miembro import Miembro
from app.routes import admin_required, instructor_required
from app.utils import bolivia_now, bolivia_date, bolivia_time
from datetime import datetime, time

clases_bp = Blueprint('clases', __name__)

@clases_bp.route('/')
@login_required
@instructor_required
def listar():
    clases = Clase.query.filter_by(activa=True).all()
    return render_template('clases/list.html', clases=clases)

@clases_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
@admin_required
def nuevo():
    if request.method == 'POST':
        clase = Clase(
            nombre=request.form.get('nombre'),
            descripcion=request.form.get('descripcion'),
            categoria=request.form.get('categoria'),
            instructor_id=request.form.get('instructor_id') or None,
            cupo_maximo=int(request.form.get('cupo_maximo', 20)),
            activa=True
        )
        db.session.add(clase)
        db.session.flush()
        dias = request.form.getlist('dia_semana[]')
        horas_ini = request.form.getlist('hora_inicio[]')
        horas_fin = request.form.getlist('hora_fin[]')
        for i in range(len(dias)):
            if dias[i] and horas_ini[i] and horas_fin[i]:
                h_ini = time.fromisoformat(horas_ini[i])
                h_fin = time.fromisoformat(horas_fin[i])
                horario = Horario(clase_id=clase.id, dia_semana=dias[i], hora_inicio=h_ini, hora_fin=h_fin)
                db.session.add(horario)
        db.session.commit()
        flash('Clase creada', 'success')
        return redirect(url_for('clases.listar'))
    instructores = Instructor.query.filter_by(activo=True).all()
    return render_template('clases/form.html', clase=None, instructores=instructores, dias_semana=DIAS_SEMANA)

@clases_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar(id):
    clase = Clase.query.get_or_404(id)
    if request.method == 'POST':
        clase.nombre = request.form.get('nombre')
        clase.descripcion = request.form.get('descripcion')
        clase.categoria = request.form.get('categoria')
        clase.instructor_id = request.form.get('instructor_id') or None
        clase.cupo_maximo = int(request.form.get('cupo_maximo', 20))
        db.session.commit()
        flash('Clase actualizada', 'success')
        return redirect(url_for('clases.listar'))
    instructores = Instructor.query.filter_by(activo=True).all()
    return render_template('clases/form.html', clase=clase, instructores=instructores, dias_semana=DIAS_SEMANA)

@clases_bp.route('/eliminar/<int:id>')
@login_required
@admin_required
def eliminar(id):
    clase = Clase.query.get_or_404(id)
    clase.activa = False
    db.session.commit()
    flash('Clase desactivada', 'success')
    return redirect(url_for('clases.listar'))

@clases_bp.route('/checkin/<int:clase_id>', methods=['GET', 'POST'])
@login_required
@instructor_required
def checkin(clase_id):
    clase = Clase.query.get_or_404(clase_id)
    if request.method == 'POST':
        miembro_id = request.form.get('miembro_id')
        miembro = Miembro.query.get(miembro_id)
        if miembro and miembro.estado == 'activo':
            exists = Asistencia.query.filter_by(
                miembro_id=miembro.id, clase_id=clase.id,
                fecha=bolivia_date()
            ).first()
            if not exists:
                asistencia = Asistencia(
                    miembro_id=miembro.id, clase_id=clase.id,
                    fecha=bolivia_date(),
                    hora_checkin=bolivia_time(),
                    asistio=True
                )
                db.session.add(asistencia)
                db.session.commit()
                flash(f'Check-in registrado para {miembro.nombre_completo}', 'success')
            else:
                flash(f'{miembro.nombre_completo} ya tiene check-in hoy', 'warning')
        else:
            flash('Miembro no encontrado o inactivo', 'danger')
        return redirect(url_for('clases.checkin', clase_id=clase.id))
    asistencias_hoy = Asistencia.query.filter_by(
        clase_id=clase.id, fecha=bolivia_date()
    ).all()
    miembros_activos = Miembro.query.filter_by(estado='activo').all()
    return render_template('clases/checkin.html', clase=clase, asistencias=asistencias_hoy, miembros=miembros_activos)
