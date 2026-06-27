import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

import app.models
from app.models.usuario import Usuario

def create_app(config_name='default'):
    flask_app = Flask(__name__)
    flask_app.config.from_object(config.get(config_name, config['default']))
    config[config_name].init_app(flask_app)

    db.init_app(flask_app)
    login_manager.init_app(flask_app)

    @login_manager.user_loader
    def load_user(user_id):
        from sqlalchemy.orm import joinedload
        return Usuario.query.options(joinedload(Usuario.rol)).get(int(user_id))

    from app.routes.auth import auth_bp
    from app.routes.miembros import miembros_bp
    from app.routes.membresias import membresias_bp
    from app.routes.clases import clases_bp
    from app.routes.instructores import instructores_bp
    from app.routes.pagos import pagos_bp
    from app.routes.asistencia import asistencia_bp
    from app.routes.admin import admin_bp
    from app.routes.instructor import instructor_bp
    from app.routes.cliente import cliente_bp
    from app.routes.promociones import promociones_bp

    flask_app.register_blueprint(auth_bp)
    flask_app.register_blueprint(miembros_bp, url_prefix='/miembros')
    flask_app.register_blueprint(membresias_bp, url_prefix='/membresias')
    flask_app.register_blueprint(clases_bp, url_prefix='/clases')
    flask_app.register_blueprint(instructores_bp, url_prefix='/instructores')
    flask_app.register_blueprint(pagos_bp, url_prefix='/pagos')
    flask_app.register_blueprint(asistencia_bp, url_prefix='/asistencia')
    flask_app.register_blueprint(admin_bp, url_prefix='/admin')
    flask_app.register_blueprint(instructor_bp, url_prefix='/instructor')
    flask_app.register_blueprint(cliente_bp, url_prefix='/cliente')
    flask_app.register_blueprint(promociones_bp, url_prefix='/promociones')

    os.makedirs(os.path.join(flask_app.root_path, 'static', 'uploads', 'comprobantes'), exist_ok=True)
    os.makedirs(os.path.join(flask_app.root_path, 'static', 'img'), exist_ok=True)

    with flask_app.app_context():
        db.create_all()

        from app.models.roles import Rol
        from sqlalchemy.exc import IntegrityError
        try:
            if not Rol.query.first():
                roles = [Rol(nombre=r) for r in ['admin', 'instructor', 'cliente']]
                for r in roles:
                    db.session.add(r)
                db.session.commit()

            if not Usuario.query.first():
                admin_rol = Rol.query.filter_by(nombre='admin').first()
                if admin_rol:
                    admin = Usuario(
                        username='Brayan',
                        email='admin@gymmanager.com',
                        rol_id=admin_rol.id,
                        activo=True
                    )
                    admin.set_password('2005')
                    db.session.add(admin)
                    db.session.commit()
        except IntegrityError:
            db.session.rollback()

    return flask_app
