from fastapi import APIRouter, Query, Path, HTTPException
from typing import List
from app.services import causas_services as causas_service
from app.models import schemas

router = APIRouter()

@router.get(
    "/ranking/riesgo",
    response_model=List[schemas.RankingItem],
    summary="Obtiene el Top N del Ranking de Riesgo Mensual",
    tags=["KPIs"]
)
def get_ranking_riesgo(
    periodo: str = Query(
        ..., 
        description="Periodo en formato YYYY-MM", 
        regex=r"^\d{4}-\d{2}$" # Valida el formato
    ),
    top_n: int = Query(
    10, 
    description="Número de ASINs a devolver", 
    gt=0, 
    le=2000  # <-- Aumentamos el límite permitido a 2000
)
):
    """
    Devuelve una lista de los N productos (ASINs) con mayor
    índice de riesgo para un periodo determinado.
    - **periodo**: El mes a consultar (ej. "2023-09").
    - **top_n**: Cuántos items del ranking devolver (default 10).
    """
    try:
        # 1. Llama al 'service' para hacer el trabajo
        ranking_data = causas_service.get_ranking_kpi(periodo, top_n)
        
        if not ranking_data:
            raise HTTPException(
                status_code=404, 
                detail=f"No se encontraron datos de ranking para el periodo: {periodo}"
            )
        
        # 2. FastAPI valida automáticamente la salida con 'response_model'
        return ranking_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/productos/{asin}/mapa-causas",
    response_model=schemas.MapaCausasResponse,
    summary="Obtiene el Mapa de Causas para un ASIN específico",
    tags=["KPIs"]
)
def get_mapa_de_causas(
    asin: str = Path(..., description="El ASIN del producto"),
    periodo: str = Query(
        ..., 
        description="Periodo en formato YYYY-MM", 
        regex=r"^\d{4}-\d{2}$"
    )
):
    """
    Devuelve las causas de reseñas negativas (1-2 estrellas)
    para un producto (ASIN) y un mes (periodo) específicos.
    """
    try:
        # 1. Llama al 'service'
        causas_data = causas_service.get_causas_kpi(periodo, asin)
        
        if not causas_data or not causas_data.get("mapa_causas"):
            raise HTTPException(
                status_code=404, 
                detail=f"No se encontraron causas para ASIN: {asin}, Periodo: {periodo}"
            )
        
        # 2. FastAPI valida la respuesta
        return causas_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/productos/{asin}/evidencia",
    response_model=List[schemas.EvidenciaItem],
    summary="Obtiene reseñas de evidencia para un ASIN y una causa",
    tags=["KPIs"]
)
def get_evidencia_textual(
    asin: str = Path(..., description="El ASIN del producto"),
    periodo: str = Query(
        ..., 
        description="Periodo en formato YYYY-MM", 
        regex=r"^\d{4}-\d{2}$"
    ),
    causa: str = Query(
        ..., 
        description="La causa a filtrar (ej. 'no_funciona', 'baja_calidad')"
    )
):
    """
    Devuelve un máximo de 5 fragmentos de reseñas negativas
    que coinciden con un ASIN, un mes y una causa específica.
    """
    try:
        # 1. Llama al 'service'
        evidencia_data = causas_service.get_evidencia_kpi(periodo, asin, causa)
        
        if not evidencia_data:
            raise HTTPException(
                status_code=404, 
                detail=f"No se encontró evidencia para ASIN: {asin}, Causa: {causa}"
            )
        
        # 2. FastAPI valida la respuesta
        return evidencia_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))