import pandas as pd
import pyarrow.parquet as pq
import pyarrow.fs as fs
from app.core.config import (
    USE_HDFS, HDFS_HOST, HDFS_PORT, 
    KPI_RANKING_PATH, KPI_CAUSAS_PATH, SILVER_EVIDENCIA_PATH
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Conexión Condicional ---
hdfs_fs = None

if USE_HDFS:
    try:
        hdfs_fs = fs.HadoopFileSystem(host=HDFS_HOST, port=HDFS_PORT)
        logger.info(f"Conectado a HDFS globalmente.")
    except Exception as e:
        logger.error(f"Error crítico conectando a HDFS: {e}")

def leer_dataset(path: str, periodo: str = None) -> pd.DataFrame:
    """
    Función inteligente que lee Parquet desde HDFS o Disco Local.
    """
    try:
        target_path = path
        filesystem = None # Por defecto (local), pyarrow usa el sistema de archivos del OS

        # Si filtramos por periodo (dt=YYYY-MM)
        if periodo:
            # En Parquet particionado, la ruta es .../carpeta/dt=2023-09/
            # Ojo: En Windows local, a veces pyarrow prefiere leer la raíz y filtrar
            target_path = f"{path}/dt={periodo}"
        
        if USE_HDFS:
            if hdfs_fs is None:
                 raise ConnectionError("HDFS no está conectado.")
            filesystem = hdfs_fs
            # En HDFS la ruta completa ya incluye el protocolo hdfs:// si viene del config,
            # pero pyarrow.fs.HadoopFileSystem a veces prefiere la ruta relativa.
            # Para simplificar, pasamos el objeto filesystem explícito.
        
        # Leemos
        logger.info(f"Leyendo desde: {target_path} | FS: {'HDFS' if USE_HDFS else 'Local'}")
        
        dataset = pq.ParquetDataset(target_path, filesystem=filesystem)
        
        # .read() devuelve una tabla pyarrow, .to_pandas() la convierte
        df = dataset.read().to_pandas()
        
        # Si estamos en local y leemos una partición específica, 
        # a veces la columna 'dt' se pierde (porque está en el nombre de la carpeta).
        # La re-agregamos manualmente si falta y tenemos el periodo.
        if periodo and 'dt' not in df.columns:
            df['dt'] = periodo
            
        return df

    except Exception as e:
        logger.error(f"Error leyendo datos en {path}: {e}")
        return pd.DataFrame()

# --- Funciones de Negocio (Sin cambios mayores) ---

def obtener_ranking(periodo: str) -> pd.DataFrame:
    return leer_dataset(KPI_RANKING_PATH, periodo)

def obtener_mapa_causas(periodo: str, asin: str) -> pd.DataFrame:
    # Leemos todo el mes
    df = leer_dataset(KPI_CAUSAS_PATH, periodo)
    if df.empty: return df
    # Filtramos en memoria (pandas)
    return df[df['asin'] == asin]

def obtener_evidencia(periodo: str, asin: str, causa: str) -> pd.DataFrame:
    # Nota: Si no tienes la data 'silver' descargada en local, esto devolverá vacío en Windows.
    # Es normal durante el desarrollo si solo te pasaron los KPIs.
    df = leer_dataset(SILVER_EVIDENCIA_PATH, periodo)
    if df.empty: return df
    
    return df[
        (df['asin'] == asin) &
        (df['cause'] == causa) &
        (df['overall'].isin([1, 2]))
    ].head(5)