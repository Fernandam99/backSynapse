import re
from datetime import datetime, date

def validate_email(email):
    pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    if re.match(pattern, email):
        return True, "Email válido"
    return False, "Email inválido"

def validate_password(password):
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"
    if not re.search(r"[A-Z]", password):
        return False, "La contraseña debe contener al menos una letra mayúscula"
    if not re.search(r"[a-z]", password):
        return False, "La contraseña debe contener al menos una letra minúscula"
    if not re.search(r"[0-9]", password):
        return False, "La contraseña debe contener al menos un número"
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "La contraseña debe contener al menos un carácter especial"
    return True, "Contraseña válida y segura"

def validate_duration(duration):
    try:
        duration = int(duration)
        if duration <= 0 or duration > 480:
            return False, "La duración debe estar entre 1 y 480 minutos"
        return True, "Duración válida"
    except (ValueError, TypeError):
        return False, "La duración debe ser un número entero"

def validate_date(date_string, format='%Y-%m-%d'):
    try:
        datetime.strptime(date_string, format)
        return True, "Fecha válida"
    except ValueError:
        return False, f"Formato de fecha inválido. Use {format}"

def validate_priority(priority):
    valid_priorities = ['baja', 'media', 'alta']
    if priority.lower() not in valid_priorities:
        return False, f"Prioridad debe ser una de: {', '.join(valid_priorities)}"
    return True, "Prioridad válida"

def validate_pomodoro_cycles(cycles):
    try:
        cycles = int(cycles)
        if cycles < 1 or cycles > 12:
            return False, "Los ciclos deben estar entre 1 y 12"
        return True, "Número de ciclos válido"
    except (ValueError, TypeError):
        return False, "Los ciclos deben ser un número entero"
