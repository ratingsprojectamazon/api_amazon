import os
# --- INTERRUPTOR DE MODO ---
# Si esta variable de entorno existe, usaremos HDFS. Si no, Local.
# En la VM la definirán en el docker-compose o .env
USE_HDFS = os.getenv("USE_HDFS", "False").lower() == "true"

# Valores por defecto para evitar errores de importación
HDFS_HOST = "localhost"
HDFS_PORT = 9000

if USE_HDFS:
    # --- CONFIGURACIÓN PRODUCCIÓN (HDFS) ---
    HDFS_HOST = os.getenv("HDFS_HOST", "localhost")
    HDFS_PORT = int(os.getenv("HDFS_PORT", 9000))
    
    BASE_PATH = "hdfs://localhost:9000/datalake/gold/results"
    SILVER_PATH = "hdfs://localhost:9000/datalake/silver/amazon/electronics/reviews_clean_2023/"
    
    print(f"🟢 MODO PRODUCCIÓN: Conectando a HDFS en {HDFS_HOST}:{HDFS_PORT}")

else:
    # --- CONFIGURACIÓN DESARROLLO (Windows Local) ---
    
    # Definimos estos como None explícitamente para que gold_reader no se confunda,
    # aunque ya tienen valores por defecto arriba.
    HDFS_HOST = None 
    HDFS_PORT = None

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    LOCAL_DATA_DIR = os.path.join(BASE_DIR, "local_data", "gold", "results")
    
    BASE_PATH = LOCAL_DATA_DIR
    # Ruta dummy para silver en local si no tienes la data
    SILVER_PATH = os.path.join(BASE_DIR, "local_data", "silver") 

    print(f"🟡 MODO DESARROLLO: Leyendo archivos locales desde {BASE_PATH}")

# Rutas Finales (Agnósticas)
KPI_RANKING_PATH = f"{BASE_PATH}/ranking_riesgo_mensual"
KPI_CAUSAS_PATH = f"{BASE_PATH}/mapa_causas_mensual"
SILVER_EVIDENCIA_PATH = SILVER_PATH