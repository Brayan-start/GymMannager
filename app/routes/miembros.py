from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import db
from app.models.miembro import Miembro
from app.models.membresia import Membresia
from app.models.tipo_membresia import TipoMembresia
from app.models.pago import Pago
from app.models.asistencia import Asistencia
from app.models.usuario import Usuario
from app.models.roles import Rol
from app.routes import admin_required, instructor_required
from datetime import datetime, timedelta, date
from sqlalchemy import func

miembros_bp = Blueprint('miembros', __name__)

@miembros_bp.route('/')
@login_required
@admin_required
def listar():
    query = Miembro.query
    search = request.args.get('search', '')
    estado = request.args.get('estado', '')
    if search:
        query = query.filter(
            db.or_(
                Miembro.nombre.ilike(f'%{search}%'),
                Miembro.apellido.ilike(f'%{search}%'),
                Miembro.ci.ilike(f'%{search}%'),
                Miembro.telefono.ilike(f'%{search}%')
            )
        )
    if estado:
        query = query.filter_by(estado=estado)
    miembros = query.order_by(Miembro.fecha_registro.desc()).all()
    return render_template('miembros/list.html', miembros=miembros, search=search, estado=estado, now=datetime.utcnow())

@miembros_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
@admin_required
def nuevo():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        apellido = request.form.get('apellido', '').strip()
        if not nombre or not apellido:
            flash('Nombre y apellido son obligatorios', 'danger')
            return render_template('miembros/form.html', miembro=None)

        miembro = Miembro(
            nombre=nombre,
            apellido=apellido,
            ci=request.form.get('ci', '').strip(),
            email=request.form.get('email', '').strip(),
            telefono=request.form.get('telefono', '').strip(),
            direccion=request.form.get('direccion', '').strip(),
            fecha_nacimiento=datetime.strptime(request.form.get('fecha_nacimiento'), '%Y-%m-%d').date() if request.form.get('fecha_nacimiento') else None
        )

        crear_usuario = request.form.get('crear_usuario') == 'on'
        if crear_usuario:
            username = request.form.get('username', '').strip()
            email = request.form.get('email_reg', '').strip()
            password = request.form.get('password', '')
            if username and password:
                if Usuario.query.filter_by(username=username).first():
                    flash('El nombre de usuario ya existe', 'danger')
                    return render_template('miembros/form.html', miembro=None)
                rol_cliente = Rol.query.filter_by(nombre='cliente').first()
                user = Usuario(username=username, email=email or f'{username}@gymmanager.com', rol_id=rol_cliente.id, activo=True)
                user.set_password(password)
                db.session.add(user)
                db.session.flush()
                miembro.usuario_id = user.id

        db.session.add(miembro)
        db.session.commit()
        flash('Miembro registrado correctamente', 'success')
        return redirect(url_for('miembros.listar'))
    return render_template('miembros/form.html', miembro=None)

@miembros_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar(id):
    miembro = Miembro.query.get_or_404(id)
    if request.method == 'POST':
        miembro.nombre = request.form.get('nombre', '').strip()
        miembro.apellido = request.form.get('apellido', '').strip()
        miembro.ci = request.form.get('ci', '').strip()
        miembro.email = request.form.get('email', '').strip()
        miembro.telefono = request.form.get('telefono', '').strip()
        miembro.direccion = request.form.get('direccion', '').strip()
        miembro.estado = request.form.get('estado', 'activo')
        fecha_nac = request.form.get('fecha_nacimiento')
        if fecha_nac:
            miembro.fecha_nacimiento = datetime.strptime(fecha_nac, '%Y-%m-%d').date()
        db.session.commit()
        flash('Miembro actualizado correctamente', 'success')
        return redirect(url_for('miembros.listar'))
    return render_template('miembros/form.html', miembro=miembro)

@miembros_bp.route('/ver/<int:id>')
@login_required
@admin_required
def ver(id):
    miembro = Miembro.query.get_or_404(id)
    membresias = miembro.membresias.all()
    pagos = miembro.pagos.limit(10).all()
    membresia_activa = miembro.membresia_activa
    dias_restantes = None
    if membresia_activa:
        dias_restantes = (membresia_activa.fecha_fin - datetime.utcnow()).days
    asistencias_mes = Asistencia.query.filter(
        Asistencia.miembro_id == miembro.id,
        func.date(Asistencia.fecha) >= date.today().replace(day=1)
    ).count()
    return render_template('miembros/view.html',
        miembro=miembro, membresias=membresias, pagos=pagos,
        membresia_activa=membresia_activa, dias_restantes=dias_restantes,
        asistencias_mes=asistencias_mes, now=datetime.utcnow())

@miembros_bp.route('/eliminar/<int:id>')
@login_required
@admin_required
def eliminar(id):
    miembro = Miembro.query.get_or_404(id)
    miembro.estado = 'inactivo'
    db.session.commit()
    flash('Miembro desactivado', 'success')
    return redirect(url_for('miembros.listar'))
