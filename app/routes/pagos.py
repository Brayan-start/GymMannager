import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models.pago import Pago, METODOS_PAGO, ESTADOS_PAGO
from app.models.miembro import Miembro
from app.models.tipo_membresia import TipoMembresia
from app.models.membresia import Membresia
from app.routes import admin_required
from datetime import datetime, timedelta

pagos_bp = Blueprint('pagos', __name__)

UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads', 'comprobantes')
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'pdf'}
MAX_FILE_SIZE = 5 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@pagos_bp.route('/')
@login_required
@admin_required
def listar():
    query = Pago.query
    search = request.args.get('search', '')
    estado = request.args.get('estado', '')
    if search:
        query = query.join(Miembro).filter(
            db.or_(
                Miembro.nombre.ilike(f'%{search}%'),
                Miembro.apellido.ilike(f'%{search}%')
            )
        )
    if estado:
        query = query.filter_by(estado=estado)
    pagos = query.order_by(Pago.fecha_pago.desc()).all()
    return render_template('pagos/list.html', pagos=pagos, search=search, estado=estado)

@pagos_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
@admin_required
def nuevo():
    if request.method == 'POST':
        miembro_id = request.form.get('miembro_id')
        tipo_membresia_id = request.form.get('tipo_membresia_id')
        tipo = TipoMembresia.query.get(tipo_membresia_id)
        metodo = request.form.get('metodo_pago', 'efectivo')
        monto_recibido = float(request.form.get('monto', tipo.precio if tipo else 0))
        precio = tipo.precio if tipo else monto_recibido

        pago = Pago(
            miembro_id=miembro_id,
            tipo_membresia_id=tipo_membresia_id,
            monto=monto_recibido,
            metodo_pago=metodo,
            estado='pendiente' if metodo == 'qr' else 'pagado',
            referencia=request.form.get('referencia', '')
        )

        if metodo == 'qr':
            file = request.files.get('comprobante')
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(f'comprobante_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}_{miembro_id}.{file.filename.rsplit(".", 1)[1].lower()}')
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                pago.comprobante_url = f'uploads/comprobantes/{filename}'
            else:
                pago.comprobante_url = None

        db.session.add(pago)
        db.session.flush()

        if metodo == 'efectivo':
            if tipo:
                dias = tipo.duracion_dias
                fecha_inicio = datetime.utcnow()
                fecha_fin = fecha_inicio + timedelta(days=dias)
                membresia = Membresia(
                    miembro_id=miembro_id,
                    tipo_id=tipo.id,
                    fecha_inicio=fecha_inicio,
                    fecha_fin=fecha_fin,
                    estado='activa'
                )
                db.session.add(membresia)
                db.session.flush()
                pago.membresia_id = membresia.id

            miembro = Miembro.query.get(miembro_id)
            if miembro:
                miembro.estado = 'activo'

            cambio = monto_recibido - precio
            db.session.commit()
            if cambio > 0:
                flash(f'Pago registrado. Membresía activada. Cambio: {cambio:.2f} Bs.', 'success')
            else:
                flash('Pago registrado. Membresía activada.', 'success')
        else:
            db.session.commit()
            flash('Pago registrado. Pendiente de verificación del comprobante.', 'warning')

        return redirect(url_for('pagos.listar'))

    miembros = Miembro.query.all()
    tipos = TipoMembresia.query.filter_by(activo=True).all()
    return render_template('pagos/form.html', pago=None, miembros=miembros, tipos=tipos, metodos=METODOS_PAGO, estados=ESTADOS_PAGO)

@pagos_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar(id):
    pago = Pago.query.get_or_404(id)
    if request.method == 'POST':
        pago.monto = float(request.form.get('monto'))
        pago.metodo_pago = request.form.get('metodo_pago')
        pago.referencia = request.form.get('referencia')
        db.session.commit()
        flash('Pago actualizado', 'success')
        return redirect(url_for('pagos.listar'))
    miembros = Miembro.query.all()
    tipos = TipoMembresia.query.filter_by(activo=True).all()
    return render_template('pagos/form.html', pago=pago, miembros=miembros, tipos=tipos, metodos=METODOS_PAGO, estados=ESTADOS_PAGO)

@pagos_bp.route('/eliminar/<int:id>')
@login_required
@admin_required
def eliminar(id):
    pago = Pago.query.get_or_404(id)
    db.session.delete(pago)
    db.session.commit()
    flash('Pago eliminado', 'success')
    return redirect(url_for('pagos.listar'))

@pagos_bp.route('/pendientes')
@login_required
@admin_required
def pendientes():
    pagos = Pago.query.filter_by(estado='pendiente').order_by(Pago.fecha_pago.desc()).all()
    return render_template('admin/pagos_pendientes.html', pagos=pagos)

@pagos_bp.route('/aprobar/<int:id>', methods=['POST'])
@login_required
@admin_required
def aprobar(id):
    pago = Pago.query.get_or_404(id)
    pago.estado = 'pagado'
    pago.fecha_verificacion = datetime.utcnow()
    pago.verificado_por = current_user.id

    if pago.tipo_membresia_id:
        tipo = TipoMembresia.query.get(pago.tipo_membresia_id)
        if tipo:
            fecha_inicio = datetime.utcnow()
            fecha_fin = fecha_inicio + timedelta(days=tipo.duracion_dias)
            membresia = Membresia(
                miembro_id=pago.miembro_id,
                tipo_id=tipo.id,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                estado='activa'
            )
            db.session.add(membresia)
            db.session.flush()
            pago.membresia_id = membresia.id

    miembro = Miembro.query.get(pago.miembro_id)
    if miembro:
        miembro.estado = 'activo'

    db.session.commit()
    flash(f'Pago #{pago.id} aprobado. Membresía activada.', 'success')
    return redirect(url_for('pagos.pendientes'))

@pagos_bp.route('/rechazar/<int:id>', methods=['POST'])
@login_required
@admin_required
def rechazar(id):
    pago = Pago.query.get_or_404(id)
    motivo = request.form.get('motivo_rechazo', '')
    pago.estado = 'rechazado'
    pago.motivo_rechazo = motivo
    pago.fecha_verificacion = datetime.utcnow()
    pago.verificado_por = current_user.id
    db.session.commit()
    flash(f'Pago #{pago.id} rechazado. Motivo: {motivo}', 'danger')
    return redirect(url_for('pagos.pendientes'))
