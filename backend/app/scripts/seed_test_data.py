import sys
import os
import random
from datetime import datetime, timedelta
from faker import Faker

# Agrega la raíz del proyecto al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.app import create_app
from backend.models import db, Rol, Usuario, Tarea, Tecnica, Sesion, Sala, UsuarioSala, Progreso, Recompensa, RecompensaUsuario

fake = Faker()
app = create_app()

def seed_roles():
    if not Rol.query.first():
        roles = [Rol(nombre='usuario'), Rol(nombre='administrador')]
        db.session.add_all(roles)
        db.session.commit()
        print("✓ Roles insertados")

def seed_usuarios(n=30):
    roles = Rol.query.all()
    for _ in range(n):
        usuario = Usuario(
            Username=fake.user_name(),
            correo=fake.unique.email(),
            password="12345678",  # Hash real en prod
            rol_id=random.choice(roles).id,
            ultimo_acceso=fake.date_time_between(start_date='-30d', end_date='now')
        )
        db.session.add(usuario)
    db.session.commit()
    print(f"✓ {n} Usuarios insertados")

def seed_tareas():
    usuarios = Usuario.query.all()
    for usuario in usuarios:
        for _ in range(random.randint(3, 6)):
            tarea = Tarea(
                usuario_id=usuario.id_usuario,
                titulo=fake.sentence(nb_words=4),
                descripcion=fake.text(max_nb_chars=100),
                completada=random.choice([True, False])
            )
            db.session.add(tarea)
    db.session.commit()
    print("✓ Tareas insertadas")

def seed_salas():
    usuarios = Usuario.query.all()
    for _ in range(10):
        creador = random.choice(usuarios)
        sala = Sala(
            nombre=fake.word().capitalize() + " Room",
            descripcion=fake.sentence(),
            creador_id=creador.id_usuario
        )
        db.session.add(sala)
    db.session.commit()
    print("✓ Salas insertadas")

def seed_usuarios_sala():
    salas = Sala.query.all()
    usuarios = Usuario.query.all()
    for sala in salas:
        participantes = random.sample(usuarios, k=random.randint(3, 8))
        for usuario in participantes:
            if not UsuarioSala.query.filter_by(id_usuario=usuario.id_usuario, id_sala=sala.id_sala).first():
                relacion = UsuarioSala(
                    id_usuario=usuario.id_usuario,
                    id_sala=sala.id_sala
                )
                db.session.add(relacion)
    db.session.commit()
    print("✓ Usuarios en salas insertados")

def seed_sesiones():
    usuarios = Usuario.query.all()
    tecnicas = Tecnica.query.all()
    for usuario in usuarios:
        for _ in range(random.randint(2, 5)):
            tecnica = random.choice(tecnicas)
            inicio = fake.date_time_between(start_date='-20d', end_date='now')
            fin = inicio + timedelta(minutes=tecnica.duracion_estimada)
            sesion = Sesion(
                usuario_id=usuario.id_usuario,
                tecnica_id=tecnica.id_tecnica,
                fecha_inicio=inicio,
                fecha_fin=fin,
                completada=True
            )
            db.session.add(sesion)
    db.session.commit()
    print("✓ Sesiones insertadas")

def seed_progresos():
    usuarios = Usuario.query.all()
    for usuario in usuarios:
        for dias in range(1, 6):  # últimos 5 días
            progreso = Progreso(
                usuario_id=usuario.id_usuario,
                fecha=datetime.today().date() - timedelta(days=dias),
                tareas_completadas=random.randint(0, 5),
                sesiones_completadas=random.randint(0, 3),
                puntos_acumulados=random.randint(0, 50)
            )
            db.session.add(progreso)
    db.session.commit()
    print("✓ Progresos insertados")

def seed_recompensas_usuario():
    usuarios = Usuario.query.all()
    recompensas = Recompensa.query.all()
    for usuario in usuarios:
        desbloqueadas = random.sample(recompensas, k=random.randint(1, len(recompensas)))
        for recompensa in desbloqueadas:
            if not RecompensaUsuario.query.filter_by(id_usuario=usuario.id_usuario, id_recompensa=recompensa.id_recompensa).first():
                r = RecompensaUsuario(
                    id_usuario=usuario.id_usuario,
                    id_recompensa=recompensa.id_recompensa,
                    fecha_obtenida=fake.date_time_between(start_date='-15d', end_date='now')
                )
                db.session.add(r)
    db.session.commit()
    print("✓ RecompensasUsuario insertadas")

def main():
    with app.app_context():
        seed_roles()
        seed_usuarios()
        seed_tareas()
        seed_salas()
        seed_usuarios_sala()
        seed_sesiones()
        seed_progresos()
        seed_recompensas_usuario()
        print("🎉 Datos de prueba insertados exitosamente.")

if __name__ == '__main__':
    main()