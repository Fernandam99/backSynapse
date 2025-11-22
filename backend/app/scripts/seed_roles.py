import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app import create_app
from app.models import db, Rol

app = create_app()
app.app_context().push()

roles_requeridos = ["admin", "usuario"]
for nombre_rol in roles_requeridos:
    if not Rol.query.filter_by(nombre=nombre_rol).first():
        db.session.add(Rol(nombre=nombre_rol))
        print(f"Rol '{nombre_rol}' creado.")

db.session.commit()
print("Roles base asegurados.")