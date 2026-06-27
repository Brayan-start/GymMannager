import os
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models.miembro import Miembro
from app.models.membresia import Membresia
from app.models.pago import Pago
from app.models.clase import Clase
from app.models.asistencia import Asistencia
from app.models.tipo_membresia import TipoMembresia
from app.models.instructor import Instructor
from app.models.asistencia_instructor import AsistenciaInstructor
from app.routes import admin_required
from app.utils import bolivia_now, bolivia_date
from datetime import datetime, timedelta, date
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    hoy = date.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    inicio_mes = hoy.replace(day=1)

    miembros_activos = Miembro.query.filter_by(estado='activo').count()
    miembros_vencidos = Miembro.query.filter_by(estado='vencido').count()
    miembros_inactivos = Miembro.query.filter_by(estado='inactivo').count()
    total_miembros = Miembro.query.count()

    clases_activas = Clase.query.filter_by(activa=True).count()
    instructores_activos = len(set(c.instructor_id for c in Clase.query.filter(Clase.instructor_id.isnot(None), Clase.activa == True).all()))

    ingresos_mes = db.session.query(func.sum(Pago.monto)).filter(
        Pago.estado == 'pagado',
        func.date(Pago.fecha_pago) >= inicio_mes
    ).scalar() or 0

    ingresos_semana = db.session.query(func.sum(Pago.monto)).filter(
        Pago.estado == 'pagado',
        func.date(Pago.fecha_pago) >= inicio_semana
    ).scalar() or 0

    asistencia_hoy = Asistencia.query.filter(
        func.date(Asistencia.fecha) == hoy
    ).count()

    asistencia_semana = Asistencia.query.filter(
        func.date(Asistencia.fecha) >= inicio_semana
    ).count()

    asistencias_por_clase = db.session.query(
        Clase.nombre, func.count(Asistencia.id).label('total')
    ).join(Asistencia, Asistencia.clase_id == Clase.id, isouter=True
    ).filter(
        func.date(Asistencia.fecha) >= inicio_mes
    ).group_by(Clase.id, Clase.nombre
    ).order_by(func.count(Asistencia.id).desc()).limit(5).all()

    top_clases = [{'nombre': c[0], 'total': c[1]} for c in asistencias_por_clase]

    membresias_vencidas = Membresia.query.filter(
        Membresia.fecha_fin < datetime.utcnow(),
        Membresia.estado == 'activa'
    ).count()

    ingresos_diarios = db.session.query(
        func.date(Pago.fecha_pago).label('dia'),
        func.sum(Pago.monto).label('total')
    ).filter(
        Pago.estado == 'pagado',
        func.date(Pago.fecha_pago) >= inicio_mes
    ).group_by(func.date(Pago.fecha_pago)).order_by(func.date(Pago.fecha_pago)).all()

    chart_labels = [str(i.dia) for i in ingresos_diarios]
    chart_data = [float(i.total) for i in ingresos_diarios]

    tipos_membresia = TipoMembresia.query.filter_by(activo=True).all()

    pago_instructores = 0
    instructores_activos_lista = Instructor.query.filter_by(activo=True).all()
    for i in instructores_activos_lista:
        count = AsistenciaInstructor.query.filter(
            AsistenciaInstructor.instructor_id == i.id,
            AsistenciaInstructor.estado == 'presente',
            func.date(AsistenciaInstructor.fecha) >= inicio_mes
        ).count()
        pago_instructores += count * i.tarifa_por_clase

    pagos_pendientes = Pago.query.filter_by(estado='pendiente').count()

    return render_template('admin/dashboard.html',
        miembros_activos=miembros_activos,
        miembros_vencidos=miembros_vencidos,
        miembros_inactivos=miembros_inactivos,
        total_miembros=total_miembros,
        clases_activas=clases_activas,
        instructores_activos=instructores_activos,
        ingresos_mes=ingresos_mes,
        ingresos_semana=ingresos_semana,
        asistencia_hoy=asistencia_hoy,
        asistencia_semana=asistencia_semana,
        top_clases=top_clases,
        membresias_vencidas=membresias_vencidas,
        chart_labels=chart_labels,
        chart_data=chart_data,
        tipos_membresia=tipos_membresia,
        pago_instructores=pago_instructores,
        pagos_pendientes=pagos_pendientes
    )

@admin_bp.route('/configurar-qr', methods=['GET', 'POST'])
@login_required
@admin_required
def configurar_qr():
    if request.method == 'POST':
        file = request.files.get('qr_image')
        if file and file.filename:
            filename = 'qr_gymmanager.png'
            qr_dir = os.path.join('app', 'static', 'img')
            os.makedirs(qr_dir, exist_ok=True)
            file.save(os.path.join(qr_dir, filename))
            flash('Imagen QR actualizada correctamente', 'success')
            return redirect(url_for('admin.configurar_qr'))
    qr_exists = os.path.exists(os.path.join('app', 'static', 'img', 'qr_gymmanager.png'))
    return render_template('admin/configurar_qr.html', qr_exists=qr_exists)
