import os
from app import create_app, db
from app.models.roles import Rol
from app.models.usuario import Usuario
from app.models.tipo_membresia import TipoMembresia
from app.models.instructor import Instructor
from app.models.clase import Clase
from app.models.horario import Horario
from app.models.miembro import Miembro
from app.models.membresia import Membresia
from app.models.promocion import Promocion
from datetime import datetime, timedelta, date, time

config_name = os.getenv('FLASK_ENV', 'development')
app = create_app(config_name)

with app.app_context():
    db.create_all()

    roles_data = ['admin', 'instructor', 'cliente']
    for r in roles_data:
        if not Rol.query.filter_by(nombre=r).first():
            db.session.add(Rol(nombre=r))
    db.session.commit()
    roles = {r.nombre: r for r in Rol.query.all()}

    for u in [
        ('admin', 'admin', 'admin123'),
        ('instructor1', 'instructor', 'instr123'),
        ('cliente1', 'cliente', 'cliente123'),
    ]:
        if not Usuario.query.filter_by(username=u[0]).first():
            user = Usuario(username=u[0], email=f'{u[0]}@gymmanager.com', rol_id=roles[u[1]].id, activo=True)
            user.set_password(u[2])
            db.session.add(user)
            print(f'Usuario {u[0]} creado.')
    db.session.commit()

    if TipoMembresia.query.first():
        print('La base de datos ya tiene datos principales. Omitiendo seed.')
        if not Promocion.query.first():
            promos_data = [
                {'nombre': 'Promo 2x1 Mensual', 'tipo': '2x1', 'valor': 0, 'tipo_membresia_id': 1, 'fecha_inicio': datetime.utcnow(), 'fecha_fin': datetime.utcnow() + timedelta(days=60), 'activo': True, 'descripcion': 'Paga 1 mes y llévate 2. ¡Duplica tu tiempo!'},
                {'nombre': 'Descuento Estudiante', 'tipo': 'descuento_porcentaje', 'valor': 15, 'tipo_membresia_id': None, 'fecha_inicio': datetime.utcnow(), 'fecha_fin': datetime.utcnow() + timedelta(days=90), 'activo': True, 'descripcion': '15% de descuento en cualquier plan presentando carnet estudiantil'},
                {'nombre': 'Promo Trimestral Especial', 'tipo': 'descuento_monto', 'valor': 60, 'tipo_membresia_id': 2, 'fecha_inicio': datetime.utcnow(), 'fecha_fin': datetime.utcnow() + timedelta(days=45), 'activo': True, 'descripcion': 'Trimestral de 480 Bs. a solo 420 Bs.'},
                {'nombre': 'Promo Anual', 'tipo': 'descuento_monto', 'valor': 332, 'tipo_membresia_id': 4, 'fecha_inicio': datetime.utcnow(), 'fecha_fin': datetime.utcnow() + timedelta(days=90), 'activo': True, 'descripcion': 'Plan anual 1668 Bs. (precio ya incluye descuento)'},
            ]
            for p in promos_data:
                db.session.add(Promocion(**p))
            db.session.commit()
            print('Promociones creadas.')
        print('Seed completado.')
        exit()

    tipos_data = [
        {'nombre': 'Mensual', 'precio': 200.00, 'duracion_dias': 30},
        {'nombre': 'Trimestral', 'precio': 480.00, 'duracion_dias': 90},
        {'nombre': 'Semestral', 'precio': 894.00, 'duracion_dias': 180},
        {'nombre': 'Anual', 'precio': 1668.00, 'duracion_dias': 365},
    ]
    tipos = []
    for t in tipos_data:
        tipo = TipoMembresia(**t)
        db.session.add(tipo)
        tipos.append(tipo)
    db.session.commit()
    print('Tipos de membresía creados.')

    instructor_user = Usuario.query.filter_by(username='instructor1').first()
    instructor = Instructor(
        usuario_id=instructor_user.id if instructor_user else 2,
        nombre='Carlos', apellido='López',
        telefono='555-0101', email='carlos@gymmanager.com',
        especialidad='CrossFit y Funcional', tarifa_por_clase=50.0, activo=True
    )
    db.session.add(instructor)
    db.session.commit()
    print('Instructor creado.')

    clases_data = [
        {'nombre': 'CrossFit Intensivo', 'categoria': 'CrossFit', 'instructor_id': 1, 'cupo_maximo': 20},
        {'nombre': 'Yoga Relax', 'categoria': 'Yoga', 'instructor_id': None, 'cupo_maximo': 15},
        {'nombre': 'Spinning Power', 'categoria': 'Spinning', 'instructor_id': None, 'cupo_maximo': 25},
        {'nombre': 'Zumba Fitness', 'categoria': 'Zumba', 'instructor_id': None, 'cupo_maximo': 30},
        {'nombre': 'Funcional Total', 'categoria': 'Funcional', 'instructor_id': 1, 'cupo_maximo': 20},
    ]
    for c in clases_data:
        clase = Clase(**c)
        db.session.add(clase)
        db.session.flush()
        if clase.nombre == 'CrossFit Intensivo':
            db.session.add(Horario(clase_id=clase.id, dia_semana='lunes', hora_inicio=time(7,0), hora_fin=time(8,0)))
            db.session.add(Horario(clase_id=clase.id, dia_semana='miercoles', hora_inicio=time(7,0), hora_fin=time(8,0)))
            db.session.add(Horario(clase_id=clase.id, dia_semana='viernes', hora_inicio=time(7,0), hora_fin=time(8,0)))
        elif clase.nombre == 'Yoga Relax':
            db.session.add(Horario(clase_id=clase.id, dia_semana='martes', hora_inicio=time(9,0), hora_fin=time(10,0)))
            db.session.add(Horario(clase_id=clase.id, dia_semana='jueves', hora_inicio=time(9,0), hora_fin=time(10,0)))
        elif clase.nombre == 'Spinning Power':
            db.session.add(Horario(clase_id=clase.id, dia_semana='lunes', hora_inicio=time(18,0), hora_fin=time(19,0)))
            db.session.add(Horario(clase_id=clase.id, dia_semana='martes', hora_inicio=time(18,0), hora_fin=time(19,0)))
            db.session.add(Horario(clase_id=clase.id, dia_semana='jueves', hora_inicio=time(18,0), hora_fin=time(19,0)))
        elif clase.nombre == 'Zumba Fitness':
            db.session.add(Horario(clase_id=clase.id, dia_semana='sabado', hora_inicio=time(10,0), hora_fin=time(11,0)))
        elif clase.nombre == 'Funcional Total':
            db.session.add(Horario(clase_id=clase.id, dia_semana='lunes', hora_inicio=time(10,0), hora_fin=time(11,0)))
            db.session.add(Horario(clase_id=clase.id, dia_semana='viernes', hora_inicio=time(10,0), hora_fin=time(11,0)))
    db.session.commit()
    print('Clases y horarios creados.')

    miembros_data = [
        {'nombre': 'Ana', 'apellido': 'Martínez', 'ci': '1234567', 'email': 'ana@email.com', 'telefono': '700-1001', 'estado': 'activo'},
        {'nombre': 'Pedro', 'apellido': 'García', 'ci': '2345678', 'email': 'pedro@email.com', 'telefono': '700-1002', 'estado': 'activo'},
        {'nombre': 'María', 'apellido': 'Hernández', 'ci': '3456789', 'email': 'maria@email.com', 'telefono': '700-1003', 'estado': 'activo'},
        {'nombre': 'Juan', 'apellido': 'Rodríguez', 'ci': '4567890', 'email': 'juan@email.com', 'telefono': '700-1004', 'estado': 'vencido'},
        {'nombre': 'Laura', 'apellido': 'Díaz', 'ci': '5678901', 'email': 'laura@email.com', 'telefono': '700-1005', 'estado': 'activo'},
    ]
    for m in miembros_data:
        db.session.add(Miembro(**m))
    db.session.commit()
    print('Miembros creados.')

    for i in range(1, 4):
        membresia = Membresia(
            miembro_id=i, tipo_id=1,
            fecha_inicio=datetime.utcnow() - timedelta(days=15),
            fecha_fin=datetime.utcnow() + timedelta(days=15),
            estado='activa'
        )
        db.session.add(membresia)
    db.session.commit()
    print('Membresías asignadas.')

    promos_data = [
        {
            'nombre': 'Promo 2x1 Mensual',
            'tipo': '2x1',
            'valor': 0,
            'tipo_membresia_id': 1,
            'fecha_inicio': datetime.utcnow(),
            'fecha_fin': datetime.utcnow() + timedelta(days=60),
            'activo': True,
            'descripcion': 'Paga 1 mes y llévate 2. ¡Duplica tu tiempo!'
        },
        {
            'nombre': 'Descuento Estudiante',
            'tipo': 'descuento_porcentaje',
            'valor': 15,
            'tipo_membresia_id': None,
            'fecha_inicio': datetime.utcnow(),
            'fecha_fin': datetime.utcnow() + timedelta(days=90),
            'activo': True,
            'descripcion': '15% de descuento en cualquier plan presentando carnet estudiantil'
        },
        {
            'nombre': 'Promo Trimestral Especial',
            'tipo': 'descuento_monto',
            'valor': 60,
            'tipo_membresia_id': 2,
            'fecha_inicio': datetime.utcnow(),
            'fecha_fin': datetime.utcnow() + timedelta(days=45),
            'activo': True,
            'descripcion': 'Trimestral de 480 Bs. a solo 420 Bs.'
        },
        {
            'nombre': 'Promo Anual',
            'tipo': 'descuento_monto',
            'valor': 332,
            'tipo_membresia_id': 4,
            'fecha_inicio': datetime.utcnow(),
            'fecha_fin': datetime.utcnow() + timedelta(days=90),
            'activo': True,
            'descripcion': 'Plan anual 1668 Bs. (precio ya incluye descuento)'
        },
    ]
    for p in promos_data:
        promo = Promocion(**p)
        db.session.add(promo)
    db.session.commit()
    print('Promociones creadas.')

    from app.models.asistencia_instructor import AsistenciaInstructor
    from app.utils import bolivia_date
    hoy = bolivia_date()
    for dia in range(1, min(20, hoy.day + 1)):
        asinst = AsistenciaInstructor(
            instructor_id=1, clase_id=1 if dia % 2 == 0 else 5,
            fecha=hoy.replace(day=dia),
            estado='presente'
        )
        db.session.add(asinst)
    db.session.commit()
    print(f'Asistencias instructor creadas (días 1-{min(19, hoy.day)}).')

    print('\n=== Seed completado ===')
    print('Usuario admin: admin / admin123')
    print('Usuario instructor: instructor1 / instr123')
    print('Usuario cliente: cliente1 / cliente123')
