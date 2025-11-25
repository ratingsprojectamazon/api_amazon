import pandas as pd
from app.data_access import gold_reader
import logging

logger = logging.getLogger(__name__)

def get_ranking_kpi(periodo: str, top_n: int = 10) -> list:
    """
    Obtiene el ranking de riesgo y lo formatea como una lista de diccionarios.
    """
    try:
        # 1. Llama a la capa data_access para obtener los datos de HDFS
        df_ranking = gold_reader.obtener_ranking(periodo)

        # 2. Maneja el caso de que no haya datos
        if df_ranking.empty:
            logger.warn(f"No se encontraron datos de ranking para el periodo: {periodo}")
            return []

        # 3. Lógica de Negocio:
        #    - Ordenar por el ranking (el pipeline ya lo hizo, pero aseguramos)
        #    - Tomar el Top N
        #    - Formatear para JSON
        df_final = df_ranking.sort_values(by="risk_rank").head(top_n)

        # Convertir NaN (Not a Number) a None para que sea JSON válido
        df_final = df_final.where(pd.notnull(df_final), None)

        # 4. Transformar a un formato de lista para el JSON
        #    ej: [{'asin': 'B0...', 'risk_rank': 1, ...}, {...}]
        return df_final.to_dict('records')

    except Exception as e:
        logger.error(f"Error en la capa de servicio (get_ranking_kpi): {e}")
        return []

def get_causas_kpi(periodo: str, asin: str) -> dict:
    """
    Obtiene el mapa de causas para un ASIN y lo formatea como un diccionario.
    """
    try:
        # 1. Llama a la capa data_access
        df_causas = gold_reader.obtener_mapa_causas(periodo, asin)

        # 2. Maneja el caso de que no haya datos
        if df_causas.empty:
            logger.warn(f"No se encontraron causas para ASIN: {asin}, Periodo: {periodo}")
            return {}

        # 3. Lógica de Negocio:
        #    Pipeline con columnas pivotadas
        #    | asin | dt | no_funciona | no_compatible | baja_calidad |
        
        # Selecciona la primera fila (solo debe haber una) y la convierte a dict
        causas_dict = df_causas.iloc[0].to_dict()

        # 4. Formatear para el "Mapa de Causas"
        #    Queremos un formato: [{'causa': 'no_funciona', 'conteo': 7}, ...]
        mapa_final = []
        causas_posibles = ["no_funciona", "no_compatible", "baja_calidad"]
        
        for causa in causas_posibles:
            if causa in causas_dict:
                conteo = causas_dict.get(causa, 0)
                if conteo > 0: # Solo mostrar causas con problemas reales
                    mapa_final.append({"causa": causa, "conteo": int(conteo)})
        
        # Ordenar de más a menos problemática
        mapa_final.sort(key=lambda x: x['conteo'], reverse=True)
        
        return {
            "asin": asin,
            "periodo": periodo,
            "mapa_causas": mapa_final
        }

    except Exception as e:
        logger.error(f"Error en la capa de servicio (get_causas_kpi): {e}")
        return {}


def get_evidencia_kpi(periodo: str, asin: str, causa: str) -> list:
    """
    Obtiene los textos de evidencia y los formatea como lista.
    """
    try:
        # 1. Llama a la capa data_access
        df_evidencia = gold_reader.obtener_evidencia(periodo, asin, causa)

        # 2. Maneja el caso de que no haya datos
        if df_evidencia.empty:
            logger.warn(f"No se encontró evidencia para ASIN: {asin}, Causa: {causa}")
            return []

        # 3. Formatear para JSON
        return df_evidencia.to_dict('records')

    except Exception as e:
        logger.error(f"Error en la capa de servicio (get_evidencia_kpi): {e}")
        return []