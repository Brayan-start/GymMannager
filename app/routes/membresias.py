from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import db
from app.models.tipo_membresia import TipoMembresia
from app.models.membresia import Membresia
from app.models.miembro import Miembro
from app.models.pago import Pago
from app.models.promocion import Promocion
from app.routes import admin_required
from datetime import datetime, timedelta

membresias_bp = Blueprint('membresias', __name__)

@membresias_bp.route('/public')
def public_listar():
    tipos = TipoMembresia.query.filter_by(activo=True).all()
    return render_template('membresias/public.html', tipos=tipos)

@membresias_bp.route('/')
@login_required
@admin_required
def listar():
    tipos = TipoMembresia.query.all()
    return render_template('membresias/list.html', tipos=tipos)

@membresias_bp.route('/tipos')
@login_required
@admin_required
def listar_tipos():
    return redirect(url_for('membresias.listar'))

@membresias_bp.route('/tipos/nuevo', methods=['GET', 'POST'])
@login_required
@admin_required
def nuevo_tipo():
    if request.method == 'POST':
        tipo = TipoMembresia(
            nombre=request.form.get('nombre'),
            precio=float(request.form.get('precio')),
            duracion_dias=int(request.form.get('duracion_dias')),
            descripcion=request.form.get('descripcion'),
            activo=True
        )
        db.session.add(tipo)
        db.session.commit()
        flash('Tipo de membresía creado', 'success')
        return redirect(url_for('membresias.listar_tipos'))
    return render_template('membresias/form.html', tipo=None)

@membresias_bp.route('/tipos/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_tipo(id):
    tipo = TipoMembresia.query.get_or_404(id)
    if request.method == 'POST':
        tipo.nombre = request.form.get('nombre')
        tipo.precio = float(request.form.get('precio'))
        tipo.duracion_dias = int(request.form.get('duracion_dias'))
        tipo.descripcion = request.form.get('descripcion')
        db.session.commit()
        flash('Tipo de membresía actualizado', 'success')
        return redirect(url_for('membresias.listar_tipos'))
    return render_template('membresias/form.html', tipo=tipo)

@membresias_bp.route('/tipos/eliminar/<int:id>')
@login_required
@admin_required
def eliminar_tipo(id):
    tipo = TipoMembresia.query.get_or_404(id)
    tipo.activo = not tipo.activo
    db.session.commit()
    flash('Estado cambiado', 'success')
    return redirect(url_for('membresias.listar_tipos'))

@membresias_bp.route('/asignar/<int:miembro_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def asignar(miembro_id):
    miembro = Miembro.query.get_or_404(miembro_id)
    if request.method == 'POST':
        tipo_id = request.form.get('tipo_id')
        tipo = TipoMembresia.query.get_or_404(tipo_id)
        precio = tipo.precio
        dias = tipo.duracion_dias
        promo_id = request.form.get('promo_id')
        promo_nombre = None
        if promo_id:
            promo = Promocion.query.get(int(promo_id))
            if promo and promo.esta_activa:
                precio, dias = promo.calcular_precio_final(precio, dias)
                promo_nombre = promo.nombre
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
            metodo_pago=request.form.get('metodo_pago', 'efectivo'),
            estado='pagado',
            referencia=request.form.get('referencia', '')
        )
        db.session.add(pago)
        miembro.estado = 'activo'
        db.session.commit()
        msg = 'Membresía asignada exitosamente'
        if promo_nombre:
            msg += f' con promoción: {promo_nombre}'
        flash(msg, 'success')
        return redirect(url_for('miembros.ver', id=miembro.id))
    tipos = TipoMembresia.query.filter_by(activo=True).all()
    promos = Promocion.query.filter(Promocion.activo == True).all()
    promos_activas = [p for p in promos if p.esta_activa]
    return render_template('membresias/asignar.html', miembro=miembro, tipos=tipos, promos=promos_activas)
