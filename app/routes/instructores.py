from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from app import db
from app.models.instructor import Instructor
from app.models.asistencia_instructor import AsistenciaInstructor
from app.models.clase import Clase
from app.models.usuario import Usuario
from app.models.roles import Rol
from app.routes import admin_required
from app.utils import bolivia_now, bolivia_date
from datetime import datetime, date, timedelta
from sqlalchemy import func

instructores_bp = Blueprint('instructores', __name__)

@instructores_bp.route('/')
@login_required
@admin_required
def listar():
    instructores = Instructor.query.all()
    return render_template('instructores/list.html', instructores=instructores)

@instructores_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
@admin_required
def nuevo():
    if request.method == 'POST':
        instructor = Instructor(
            nombre=request.form.get('nombre'),
            apellido=request.form.get('apellido'),
            telefono=request.form.get('telefono'),
            email=request.form.get('email'),
            especialidad=request.form.get('especialidad'),
            tarifa_por_clase=float(request.form.get('tarifa_por_clase', 50)),
            activo=True
        )
        crear_usuario = request.form.get('crear_usuario') == 'on'
        if crear_usuario:
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            if username and password:
                rol_instructor = Rol.query.filter_by(nombre='instructor').first()
                user = Usuario(username=username, email=email, rol_id=rol_instructor.id, activo=True)
                user.set_password(password)
                db.session.add(user)
                db.session.flush()
                instructor.usuario_id = user.id
        db.session.add(instructor)
        db.session.commit()
        flash('Instructor registrado', 'success')
        return redirect(url_for('instructores.listar'))
    return render_template('instructores/form.html', instructor=None)

@instructores_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar(id):
    instructor = Instructor.query.get_or_404(id)
    if request.method == 'POST':
        instructor.nombre = request.form.get('nombre')
        instructor.apellido = request.form.get('apellido')
        instructor.telefono = request.form.get('telefono')
        instructor.email = request.form.get('email')
        instructor.especialidad = request.form.get('especialidad')
        instructor.tarifa_por_clase = float(request.form.get('tarifa_por_clase', 50))
        db.session.commit()
        flash('Instructor actualizado', 'success')
        return redirect(url_for('instructores.ver', id=instructor.id))
    return render_template('instructores/form.html', instructor=instructor)

@instructores_bp.route('/eliminar/<int:id>')
@login_required
@admin_required
def eliminar(id):
    instructor = Instructor.query.get_or_404(id)
    instructor.activo = not instructor.activo
    db.session.commit()
    flash('Estado cambiado', 'success')
    return redirect(url_for('instructores.listar'))

@instructores_bp.route('/ver/<int:id>')
@login_required
@admin_required
def ver(id):
    instructor = Instructor.query.get_or_404(id)
    hoy = bolivia_date()
    inicio_mes = hoy.replace(day=1)
    mes_anterior = (inicio_mes - timedelta(days=1)).replace(day=1)

    asistencias_mes = AsistenciaInstructor.query.filter(
        AsistenciaInstructor.instructor_id == instructor.id,
        AsistenciaInstructor.fecha >= inicio_mes,
        AsistenciaInstructor.fecha <= hoy
    ).order_by(AsistenciaInstructor.fecha.desc()).all()

    clases_dictadas_mes = AsistenciaInstructor.query.filter(
        AsistenciaInstructor.instructor_id == instructor.id,
        AsistenciaInstructor.estado == 'presente',
        AsistenciaInstructor.fecha >= inicio_mes,
        AsistenciaInstructor.fecha <= hoy
    ).count()

    dias_trabajados = db.session.query(
        func.count(func.distinct(AsistenciaInstructor.fecha))
    ).filter(
        AsistenciaInstructor.instructor_id == instructor.id,
        AsistenciaInstructor.estado == 'presente',
        AsistenciaInstructor.fecha >= inicio_mes,
        AsistenciaInstructor.fecha <= hoy
    ).scalar() or 0

    total_pagar = clases_dictadas_mes * instructor.tarifa_por_clase

    clases = Clase.query.filter_by(activa=True).all()

    return render_template('instructores/ver.html',
        instructor=instructor, asistencias=asistencias_mes,
        clases_dictadas_mes=clases_dictadas_mes,
        dias_trabajados=dias_trabajados,
        total_pagar=total_pagar, clases=clases, now=bolivia_now())

@instructores_bp.route('/registrar-asistencia/<int:id>', methods=['POST'])
@login_required
@admin_required
def registrar_asistencia(id):
    instructor = Instructor.query.get_or_404(id)
    clase_id = request.form.get('clase_id')
    estado = request.form.get('estado', 'presente')
    observacion = request.form.get('observacion', '')

    asistencia = AsistenciaInstructor(
        instructor_id=instructor.id,
        clase_id=clase_id or None,
        fecha=bolivia_date(),
        hora_entrada=bolivia_now().time(),
        estado=estado,
        observacion=observacion
    )
    db.session.add(asistencia)
    db.session.commit()
    flash(f'Asistencia registrada: {instructor.nombre_completo} - {estado}', 'success')
    return redirect(url_for('instructores.ver', id=instructor.id))

@instructores_bp.route('/reporte-pagos')
@login_required
@admin_required
def reporte_pagos():
    hoy = bolivia_date()
    mes = request.args.get('mes', hoy.month)
    anio = request.args.get('anio', hoy.year)
    try:
        mes = int(mes)
        anio = int(anio)
    except:
        mes = hoy.month
        anio = hoy.year

    inicio_mes = date(anio, mes, 1)
    if mes == 12:
        fin_mes = date(anio + 1, 1, 1) - timedelta(days=1)
    else:
        fin_mes = date(anio, mes + 1, 1) - timedelta(days=1)

    instructores = Instructor.query.filter_by(activo=True).all()
    reporte = []
    total_general = 0
    for i in instructores:
        clases_dictadas = AsistenciaInstructor.query.filter(
            AsistenciaInstructor.instructor_id == i.id,
            AsistenciaInstructor.estado == 'presente',
            AsistenciaInstructor.fecha >= inicio_mes,
            AsistenciaInstructor.fecha <= fin_mes
        ).count()
        pago_realizado = AsistenciaInstructor.query.filter(
            AsistenciaInstructor.instructor_id == i.id,
            AsistenciaInstructor.estado == 'presente',
            AsistenciaInstructor.pago_realizado == True,
            AsistenciaInstructor.fecha >= inicio_mes,
            AsistenciaInstructor.fecha <= fin_mes
        ).count()
        total = clases_dictadas * i.tarifa_por_clase
        pagado = pago_realizado * i.tarifa_por_clase
        pendiente = total - pagado
        total_general += total
        reporte.append({
            'instructor': i,
            'clases_dictadas': clases_dictadas,
            'tarifa': i.tarifa_por_clase,
            'total': total,
            'pagado': pagado,
            'pendiente': pendiente
        })

    return render_template('instructores/reporte_pagos.html',
        reporte=reporte, total_general=total_general,
        mes=mes, anio=anio, ahora=bolivia_now())

@instructores_bp.route('/marcar-pagado/<int:id>', methods=['POST'])
@login_required
@admin_required
def marcar_pagado(id):
    asistencia = AsistenciaInstructor.query.get_or_404(id)
    asistencia.pago_realizado = not asistencia.pago_realizado
    db.session.commit()
    estado = 'pagado' if asistencia.pago_realizado else 'pendiente'
    flash(f'Asistencia marcada como {estado}', 'success')
    return redirect(url_for('instructores.ver', id=asistencia.instructor_id))
