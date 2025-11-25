from pydantic import BaseModel
from typing import List, Optional

# --- Esquema para la Evidencia Textual ---
# Define la forma de una sola reseña de evidencia
class EvidenciaItem(BaseModel):
    review_id: str
    overall: int
    reviewText: str

    class Config:
        orm_mode = True  # Permite a Pydantic leer desde objetos (como DataFrames)

# --- Esquema para el Mapa de Causas ---
# Define la forma de un item en el mapa (ej. "no_funciona": 10)
class CausaItem(BaseModel):
    causa: str
    conteo: int

# Define la respuesta completa para el endpoint de /mapa-causas
class MapaCausasResponse(BaseModel):
    asin: str
    periodo: str
    mapa_causas: List[CausaItem]

# --- Esquema para el Ranking de Riesgo ---
# Define la forma de un solo item en el ranking
class RankingItem(BaseModel):
    asin: str
    dt: str
    risk_rank: int
    n_reviews: int
    n_neg: int
    pct_neg: float
    # avg_prob_neg puede ser nulo si no hay reseñas negativas
    avg_prob_neg: Optional[float] 

    class Config:
        orm_mode = True

# --- Esquema para Mensajes Genéricos ---
# Útil para enviar mensajes de error o éxito
class Message(BaseModel):
    detail: str