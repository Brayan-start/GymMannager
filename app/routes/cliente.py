import os
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models.miembro import Miembro
from app.models.membresia import Membresia
from app.models.pago import Pago
from app.models.asistencia import Asistencia
from app.models.clase import Clase
from app.models.tipo_membresia import TipoMembresia
from app.models.promocion import Promocion
from datetime import datetime, date, timedelta
from sqlalchemy import func

cliente_bp = Blueprint('cliente', __name__)

UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads', 'comprobantes')
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@cliente_bp.route('/dashboard')
@login_required
def dashboard():
    miembro = Miembro.query.filter_by(usuario_id=current_user.id).first()

    membresia_activa = None
    ultimos_pagos = []
    asistencias_recientes = []
    clases_disponibles = Clase.query.filter_by(activa=True).all()

    if miembro:
        membresia_activa = Membresia.query.filter_by(
            miembro_id=miembro.id, estado='activa'
        ).filter(Membresia.fecha_fin >= datetime.utcnow()).first()

        ultimos_pagos = Pago.query.filter_by(
            miembro_id=miembro.id
        ).order_by(Pago.fecha_pago.desc()).limit(5).all()

        asistencias_recientes = Asistencia.query.filter_by(
            miembro_id=miembro.id
        ).order_by(Asistencia.fecha.desc()).limit(10).all()

    asistencias_mes = 0
    if miembro:
        inicio_mes = date.today().replace(day=1)
        asistencias_mes = Asistencia.query.filter(
            Asistencia.miembro_id == miembro.id,
            func.date(Asistencia.fecha) >= inicio_mes
        ).count()

    return render_template('cliente/dashboard.html',
        miembro=miembro,
        membresia=membresia_activa,
        pagos=ultimos_pagos,
        asistencias=asistencias_recientes,
        asistencias_mes=asistencias_mes,
        clases=clases_disponibles
    )

@cliente_bp.route('/membresia')
@login_required
def membresia():
    miembro = Miembro.query.filter_by(usuario_id=current_user.id).first()
    membresia_activa = None
    if miembro:
        membresia_activa = Membresia.query.filter_by(
            miembro_id=miembro.id, estado='activa'
        ).filter(Membresia.fecha_fin >= datetime.utcnow()).first()
    tipos = TipoMembresia.query.filter_by(activo=True).all()
    return render_template('cliente/membresia.html',
        miembro=miembro, membresia=membresia_activa, tipos=tipos)

@cliente_bp.route('/clases')
@login_required
def clases():
    clases_disponibles = Clase.query.filter_by(activa=True).all()
    return render_template('cliente/clases.html', clases=clases_disponibles)

@cliente_bp.route('/asistencia')
@login_required
def asistencia():
    miembro = Miembro.query.filter_by(usuario_id=current_user.id).first()
    asistencias = []
    if miembro:
        asistencias = Asistencia.query.filter_by(
            miembro_id=miembro.id
        ).order_by(Asistencia.fecha.desc()).all()
    return render_template('cliente/asistencia.html', asistencias=asistencias)

@cliente_bp.route('/pagos')
@login_required
def pagos():
    miembro = Miembro.query.filter_by(usuario_id=current_user.id).first()
    pagos_list = []
    if miembro:
        pagos_list = Pago.query.filter_by(
            miembro_id=miembro.id
        ).order_by(Pago.fecha_pago.desc()).all()
    return render_template('cliente/pagos.html', pagos=pagos_list)

@cliente_bp.route('/nuevo-pago', methods=['GET', 'POST'])
@login_required
def nuevo_pago():
    miembro = Miembro.query.filter_by(usuario_id=current_user.id).first()
    if not miembro:
        miembro = Miembro(
            usuario_id=current_user.id,
            nombre=current_user.username,
            apellido='',
            email=current_user.email or '',
            estado='activo'
        )
        db.session.add(miembro)
        db.session.flush()

    if request.method == 'POST':
        tipo_id = request.form.get('tipo_membresia_id')
        metodo = request.form.get('metodo_pago', 'qr')
        tipo = TipoMembresia.query.get(tipo_id) if tipo_id else None
        monto = float(request.form.get('monto', tipo.precio if tipo else 0))

        pago = Pago(
            miembro_id=miembro.id,
            tipo_membresia_id=tipo.id if tipo else None,
            monto=monto,
            metodo_pago=metodo,
            estado='pendiente',
            referencia='Pago por cliente'
        )

        if metodo == 'qr':
            file = request.files.get('comprobante')
            if file and file.filename and allowed_file(file.filename):
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = secure_filename(f'comprobante_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}_{miembro.id}.{ext}')
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                pago.comprobante_url = f'uploads/comprobantes/{filename}'
            else:
                flash('Debes subir una imagen del comprobante de pago', 'danger')
                tipos = TipoMembresia.query.filter_by(activo=True).all()
                qr_exists = os.path.exists(os.path.join('app', 'static', 'img', 'qr_gymmanager.png'))
                return render_template('cliente/nuevo_pago.html', miembro=miembro, tipos=tipos, qr_exists=qr_exists)

        db.session.add(pago)
        db.session.commit()
        flash('Pago registrado. Tu membresía se activará cuando el administrador verifique el comprobante.', 'success')
        return redirect(url_for('cliente.pagos'))

    tipos = TipoMembresia.query.filter_by(activo=True).all()
    qr_exists = os.path.exists(os.path.join('app', 'static', 'img', 'qr_gymmanager.png'))
    return render_template('cliente/nuevo_pago.html', miembro=miembro, tipos=tipos, qr_exists=qr_exists)

@cliente_bp.route('/adquirir-membresia/<int:tipo_id>', methods=['GET', 'POST'])
@login_required
def adquirir_membresia(tipo_id):
    tipo = TipoMembresia.query.get_or_404(tipo_id)
    miembro = Miembro.query.filter_by(usuario_id=current_user.id).first()

    if not miembro:
        miembro = Miembro(
            usuario_id=current_user.id,
            nombre=current_user.username,
            apellido='',
            email=current_user.email or '',
            estado='activo'
        )
        db.session.add(miembro)
        db.session.flush()

    if request.method == 'POST':
        membresia_activa = Membresia.query.filter_by(
            miembro_id=miembro.id, estado='activa'
        ).filter(Membresia.fecha_fin >= datetime.utcnow()).first()
        if membresia_activa:
            flash('Ya tienes una membresía activa', 'warning')
            return redirect(url_for('cliente.membresia'))

        metodo = request.form.get('metodo_pago', 'efectivo')
        precio = tipo.precio
        dias = tipo.duracion_dias

        if metodo == 'efectivo':
            fecha_inicio = datetime.utcnow()
            fecha_fin = fecha_inicio + timedelta(days=dias)
            membresia = Membresia(
                miembro_id=miembro.id,
                tipo_id=tipo.id,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                estado='activa'
            )
            db.session.add(membresia)
            db.session.flush()

            pago = Pago(
                miembro_id=miembro.id,
                membresia_id=membresia.id,
                tipo_membresia_id=tipo.id,
                monto=precio,
                metodo_pago='efectivo',
                estado='pagado',
                referencia='Adquirido por web'
            )
            db.session.add(pago)
            miembro.estado = 'activo'
            db.session.commit()
            flash(f'¡Bienvenido! Tu membresía {tipo.nombre} está activa', 'success')
            return redirect(url_for('cliente.dashboard'))
        else:
            pago = Pago(
                miembro_id=miembro.id,
                tipo_membresia_id=tipo.id,
                monto=precio,
                metodo_pago='qr',
                estado='pendiente',
                referencia='Pago por QR'
            )
            file = request.files.get('comprobante')
            if file and file.filename and allowed_file(file.filename):
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = secure_filename(f'comprobante_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}_{miembro.id}.{ext}')
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                pago.comprobante_url = f'uploads/comprobantes/{filename}'
            else:
                flash('Debes subir una imagen del comprobante de pago', 'danger')
                qr_exists = os.path.exists(os.path.join('app', 'static', 'img', 'qr_gymmanager.png'))
                return render_template('cliente/adquirir_membresia.html', tipo=tipo, qr_exists=qr_exists)
            db.session.add(pago)
            db.session.commit()
            flash('Pago registrado. Tu membresía se activará cuando el administrador verifique el comprobante.', 'success')
            return redirect(url_for('cliente.pagos'))

    qr_exists = os.path.exists(os.path.join('app', 'static', 'img', 'qr_gymmanager.png'))
    return render_template('cliente/adquirir_membresia.html', tipo=tipo, qr_exists=qr_exists)
