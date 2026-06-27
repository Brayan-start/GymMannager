from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.usuario import Usuario
from app.models.roles import Rol
from app.models.tipo_membresia import TipoMembresia
from app.models.miembro import Miembro

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('auth.redirect_by_role'))
    return render_template('index.html')

@auth_bp.route('/redirect')
@login_required
def redirect_by_role():
    if current_user.is_admin():
        return redirect(url_for('admin.dashboard'))
    elif current_user.is_instructor():
        return redirect(url_for('instructor.dashboard'))
    else:
        return redirect(url_for('cliente.dashboard'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.redirect_by_role'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = Usuario.query.filter_by(username=username).first()
        if user and user.check_password(password) and user.activo:
            login_user(user)
            next_page = request.args.get('next')
            flash(f'Bienvenido, {user.username}', 'success')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('auth.redirect_by_role'))
        flash('Usuario o contraseña incorrectos', 'danger')
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        if Usuario.query.filter_by(username=username).first():
            flash('El usuario ya existe', 'danger')
            return render_template('auth/register.html')
        rol_cliente = Rol.query.filter_by(nombre='cliente').first()
        if not rol_cliente:
            rol_cliente = Rol(nombre='cliente')
            db.session.add(rol_cliente)
            db.session.commit()
        user = Usuario(
            username=username,
            email=email,
            rol_id=rol_cliente.id,
            activo=True
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
        # Auto-create Miembro record for new clients
        if rol_cliente.nombre == 'cliente':
            miembro = Miembro(
                usuario_id=user.id,
                nombre=username,
                apellido='',
                email=email,
                estado='activo'
            )
            db.session.add(miembro)
        db.session.commit()
        flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada', 'info')
    return redirect(url_for('auth.index'))
