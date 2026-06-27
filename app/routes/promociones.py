from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from app import db
from app.models.promocion import Promocion, TIPOS_PROMO
from app.models.tipo_membresia import TipoMembresia
from app.routes import admin_required
from datetime import datetime

promociones_bp = Blueprint('promociones', __name__)

@promociones_bp.route('/')
@login_required
@admin_required
def listar():
    promos = Promocion.query.order_by(Promocion.activo.desc(), Promocion.fecha_inicio.desc()).all()
    return render_template('promociones/list.html', promos=promos, now=datetime.now())

@promociones_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
@admin_required
def nuevo():
    if request.method == 'POST':
        promo = Promocion(
            nombre=request.form.get('nombre'),
            tipo=request.form.get('tipo'),
            valor=float(request.form.get('valor')),
            tipo_membresia_id=request.form.get('tipo_membresia_id') or None,
            fecha_inicio=datetime.strptime(request.form.get('fecha_inicio'), '%Y-%m-%d') if request.form.get('fecha_inicio') else datetime.utcnow(),
            fecha_fin=datetime.strptime(request.form.get('fecha_fin'), '%Y-%m-%d') if request.form.get('fecha_fin') else None,
            activo=True,
            descripcion=request.form.get('descripcion')
        )
        db.session.add(promo)
        db.session.commit()
        flash('Promoción creada exitosamente', 'success')
        return redirect(url_for('promociones.listar'))
    tipos = TipoMembresia.query.filter_by(activo=True).all()
    return render_template('promociones/form.html', promo=None, tipos=tipos, tipos_promo=TIPOS_PROMO)

@promociones_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar(id):
    promo = Promocion.query.get_or_404(id)
    if request.method == 'POST':
        promo.nombre = request.form.get('nombre')
        promo.tipo = request.form.get('tipo')
        promo.valor = float(request.form.get('valor'))
        promo.tipo_membresia_id = request.form.get('tipo_membresia_id') or None
        promo.fecha_inicio = datetime.strptime(request.form.get('fecha_inicio'), '%Y-%m-%d') if request.form.get('fecha_inicio') else promo.fecha_inicio
        promo.fecha_fin = datetime.strptime(request.form.get('fecha_fin'), '%Y-%m-%d') if request.form.get('fecha_fin') else None
        promo.descripcion = request.form.get('descripcion')
        db.session.commit()
        flash('Promoción actualizada', 'success')
        return redirect(url_for('promociones.listar'))
    tipos = TipoMembresia.query.filter_by(activo=True).all()
    return render_template('promociones/form.html', promo=promo, tipos=tipos, tipos_promo=TIPOS_PROMO)

@promociones_bp.route('/eliminar/<int:id>')
@login_required
@admin_required
def eliminar(id):
    promo = Promocion.query.get_or_404(id)
    promo.activo = not promo.activo
    db.session.commit()
    flash('Estado de promoción cambiado', 'success')
    return redirect(url_for('promociones.listar'))

@promociones_bp.route('/calcular')
@login_required
@admin_required
def calcular():
    tipo_id = request.args.get('tipo_id')
    promo_id = request.args.get('promo_id')
    if not tipo_id:
        return jsonify({'error': 'Falta tipo'})
    tipo = TipoMembresia.query.get(int(tipo_id))
    if not tipo:
        return jsonify({'error': 'Tipo no encontrado'})
    precio = tipo.precio
    dias = tipo.duracion_dias
    promo_nombre = None
    if promo_id:
        promo = Promocion.query.get(int(promo_id))
        if promo and promo.esta_activa:
            precio, dias = promo.calcular_precio_final(precio, dias)
            promo_nombre = promo.nombre
    return jsonify({
        'precio': round(precio, 2),
        'dias': dias,
        'promo_nombre': promo_nombre
    })
