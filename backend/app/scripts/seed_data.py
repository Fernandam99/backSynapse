import sys
import os

# Agrega la raíz del proyecto al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.app import create_app
from backend.models import db, Rol, Tecnica, Recompensa
import json

app = create_app()

def insertar_datos_iniciales():
    with app.app_context():
        print("Insertando datos iniciales...")
        
        # Crear roles si no existen
        if not Rol.query.first():
            roles = [
                Rol(nombre='administrador'),
                Rol(nombre='usuario')
            ]
            for rol in roles:
                db.session.add(rol)
            print("✓ Roles creados")
        
        # Crear técnicas de estudio básicas
        if not Tecnica.query.first():
            tecnicas = [
                Tecnica(nombre='Pomodoro', categoria='Gestión del tiempo', descripcion='Técnica de estudio por intervalos de 25 minutos', duracion_estimada=25),
                Tecnica(nombre='Timeboxing', categoria='Gestión del tiempo', descripcion='Asignación estricta de tiempo a tareas', duracion_estimada=30),
                Tecnica(nombre='Técnica Feynman', categoria='Comprensión', descripcion='Aprender explicando con tus propias palabras', duracion_estimada=40),
                Tecnica(nombre='Mapas mentales', categoria='Organización', descripcion='Visualizar ideas y relaciones', duracion_estimada=20),
                Tecnica(nombre='Repetición espaciada', categoria='Memorización', descripcion='Revisar contenido en intervalos crecientes', duracion_estimada=15),
                Tecnica(nombre='Método Cornell', categoria='Toma de notas', descripcion='Técnica estructurada para tomar apuntes', duracion_estimada=45),
                Tecnica(nombre='Lectura activa', categoria='Comprensión', descripcion='Leer con objetivos claros y preguntas', duracion_estimada=30),
                Tecnica(nombre='Flashcards', categoria='Memorización', descripcion='Uso de tarjetas de preguntas y respuestas', duracion_estimada=10)
            ]
            for tecnica in tecnicas:
                db.session.add(tecnica)
            print("✓ Técnicas de estudio creadas")
        
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
        
        db.session.commit()
        print("🎉 Datos iniciales insertados correctamente!")

if __name__ == '__main__':
    insertar_datos_iniciales()