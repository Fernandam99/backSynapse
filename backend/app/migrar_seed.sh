#!/bin/bash

# Cargar variables del .env
export $(grep -v '^#' .env.migrate | xargs)

# Mostrar estado
echo "Iniciando proceso de migración y seed..."

# Ejecutar migración si hay cambios
echo "Generando migración (si hay cambios)..."
flask db migrate -m "Auto-migración por cambios en modelos"

# Aplicar migraciones a la base de datos
echo "⬆Aplicando migraciones..."
flask db upgrade

# Insertar datos iniciales
echo "Ejecutando seed_data.py..."
python backend/scripts/seed_data.py

echo "Migración y seed completados correctamente."
