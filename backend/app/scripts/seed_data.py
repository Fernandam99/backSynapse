import sys
import os

# Agrega la raíz del proyecto al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app import create_app
from app.models import db
from app.models.rol import Rol
from app.models.tecnica import Tecnica
from app.models.recompensa import Recompensa
import json

app = create_app()

def insertar_datos_iniciales():
    with app.app_context():
        print("Insertando datos iniciales...")
        
        # Crear roles si no existen
        roles = {
            'admin': Rol.query.filter_by(nombre='admin').first() or Rol(nombre='admin'),
            'usuario': Rol.query.filter_by(nombre='usuario').first() or Rol(nombre='usuario')
        }
        
        for rol in roles.values():
            if rol.id is None:
                db.session.add(rol)
        db.session.commit()
        print("✓ Roles creados")
        
        # Crear usuarios si no existen
        usuarios = [
            {
                'username': 'johan_dev',
                'correo': 'johan@gmail.com',
                'password': 'holasoyivan1234.',
                'rol': 'admin'
            },
            {
                'username': 'ivan_tech',
                'correo': 'ivan@gmail.com',
                'password': 'holasoyivan1234.',
                'rol': 'admin'
            },
            {
                'username': 'mafe_design',
                'correo': 'mafe@gmail.com',
                'password': 'Synapse2023!',
                'rol': 'usuario'
            },
            {
                'username': 'carol_user',
                'correo': 'carol@gmail.com',
                'password': 'SynapseApp2023!',
                'rol': 'usuario'
            },
            {
                'username': 'daniela_92',
                'correo': 'dani92@gmail.com',
                'password': 'Focus2023!',
                'rol': 'usuario'
            },
            {
                'username': 'sebastian_dev',
                'correo': 'sebas@gmail.com',
                'password': 'DevTeam2023!',
                'rol': 'usuario'
            }
        ]

        from werkzeug.security import generate_password_hash
        from app.models.usuario import Usuario
        
        for user_data in usuarios:
            if not Usuario.query.filter_by(correo=user_data['correo']).first():
                nuevo_usuario = Usuario(
                    username=user_data['username'],
                    correo=user_data['correo'],
                    password=generate_password_hash(user_data['password']),
                    rol_id=roles[user_data['rol']].id
                )
                db.session.add(nuevo_usuario)
        db.session.commit()
        print("✓ Usuarios creados")
        
        # Crear técnicas básicas: solo Pomodoro y Meditación
        if not Tecnica.query.first():
            tecnicas = [
                Tecnica(
                    nombre='Pomodoro',
                categoria='productividad',
                descripcion='Técnica de estudio por intervalos de 25 minutos',
                duracion_estimada=25
                ),
                Tecnica(
                    nombre='Meditación',
                    categoria='bienestar',
                    descripcion='Sesiones guiadas de atención plena y respiración',
                    duracion_estimada=10
                )
            ]
        for tecnica in tecnicas:
            db.session.add(tecnica)
        db.session.commit()
        print("✓ Técnicas esenciales creadas: Pomodoro y Meditación")
        
        # Crear recompensas básicas
        if not Recompensa.query.first():
            recompensas = [
                Recompensa(
                    nombre='Primera Sesión',
                    descripcion='Completa tu primera sesión de estudio',
                    tipo='puntos',
                    valor=10,
                    requisitos={'sesiones_completadas': 1}
                ),
                Recompensa(
                    nombre='Estudiante Dedicado',
                    descripcion='Completa 10 sesiones de estudio',
                    tipo='puntos',
                    valor=50,
                    requisitos={'sesiones_completadas': 10}
                ),
                Recompensa(
                    nombre='Maratonista Mental',
                    descripcion='Estudia por 5 horas en total',
                    tipo='puntos',
                    valor=100,
                    requisitos={'tiempo_total_minutos': 300}
                ),
                Recompensa(
                    nombre='Organizador Pro',
                    descripcion='Completa 20 tareas',
                    tipo='puntos',
                    valor=75,
                    requisitos={'tareas_completadas': 20}
                ),
                Recompensa(
                    nombre='Constancia',
                    descripcion='Estudia 7 días consecutivos',
                    tipo='puntos',
                    valor=150,
                    requisitos={'dias_consecutivos': 7}
                )
            ]
            for recompensa in recompensas:
                db.session.add(recompensa)
            print("✓ Recompensas básicas creadas")
        
        from app.models.tarea import Tarea
        usuarios_db = Usuario.query.all()
        for user in usuarios_db:
            # Solo si el usuario no tiene tareas
            if not user.tareas or len(user.tareas) == 0:
                tareas = [
                    Tarea(
                        usuario_id=user.id_usuario,
                        titulo=f'Tarea 1 de {user.username}',
                        descripcion='Descripción de la tarea 1',
                        estado='pendiente',
                        prioridad='media'
                    ),
                    Tarea(
                        usuario_id=user.id_usuario,
                        titulo=f'Tarea 2 de {user.username}',
                        descripcion='Descripción de la tarea 2',
                        estado='completada',
                        prioridad='alta',
                        completada=True
                    )
                ]
                for tarea in tareas:
                    db.session.add(tarea)
        db.session.commit()
        print('✓ Tareas de ejemplo creadas para cada usuario')
        
        db.session.commit()
        print("🎉 Datos iniciales insertados correctamente!")

if __name__ == '__main__':
    insertar_datos_iniciales()