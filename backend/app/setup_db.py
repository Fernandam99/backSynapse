import sys
import os

# Asegurarse de que el directorio actual esté en sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pymysql
from backend.run import create_app
from app.models import db
from app.config import Config

# Configuración para conectar sin seleccionar base de datos
# Cambien estos valores según su configuración local
HOST = 'localhost'
PORT = 3307
USER = 'root'
PASSWORD = 'koal'
DATABASE = 'synapse_db'

def create_database():
    # Conectar al servidor MariaDB sin seleccionar base de datos
    connection = pymysql.connect(host=HOST, port=PORT, user=USER, password=PASSWORD)
    try:
        with connection.cursor() as cursor:
            # Crear la base de datos si no existe
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            print(f"Base de datos '{DATABASE}' creada o ya existente.")
        connection.commit()
    finally:
        connection.close()

def create_tables():
    # Crear la app y cargar configuración para crear tablas
    app = create_app('development')
    with app.app_context():
        db.create_all()
        print("Tablas creadas exitosamente.")

if __name__ == '__main__':
    create_database()
    create_tables()
