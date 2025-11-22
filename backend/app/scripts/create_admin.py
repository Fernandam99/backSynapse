import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import db, Usuario, Rol

def create_admin():
    app = create_app()
    with app.app_context():
        # Verificar si ya existe un admin
        admin = Usuario.query.filter_by(rol_id=1).first()
        if admin:
            print(f" Ya existe un administrador: {admin.username} ({admin.correo})")
            return

        # Asegurarse de que el rol 'administrador' exista
        rol_admin = Rol.query.filter_by(nombre='administrador').first()
        if not rol_admin:
            print(" El rol 'administrador' no existe. Ejecuta primero: python -m app.scripts.seed_roles")
            return

        # Crear usuario administrador
        admin_user = Usuario(
            username='administrador',
            correo='admin@synapse.com',
            password=generate_password_hash('admin123'),  # Ver nota abajo
            rol_id=rol_admin.id,
            activo=True
        )

        db.session.add(admin_user)
        db.session.commit()
        print(" Administrador creado:")
        print(f"   Usuario: {admin_user.username}")
        print(f"   Correo: {admin_user.correo}")
        print(f"   Contraseña: admin123")

def generate_password_hash(password):
    from werkzeug.security import generate_password_hash
    return generate_password_hash(password)

if __name__ == '__main__':
    create_admin()