#!/bin/bash
#
# Script para correr el servidor de API en modo DESARROLLO
#

echo "Iniciando servidor de API en http://localhost:8000"

# uvicorn app.main:app
#   -> app.main: El archivo main.py dentro de la carpeta app/
#   -> :app: La variable 'app = FastAPI()' dentro de ese archivo
# --host 0.0.0.0
#   -> Permite conexiones desde fuera del contenedor (o desde tu red)
# --port 8000
#   -> El puerto en el que escuchará
# --reload
#   -> Reinicia automáticamente el servidor cuando guardas cambios en el código

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload