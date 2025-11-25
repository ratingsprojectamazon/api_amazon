from fastapi import FastAPI
from app.services import causas_services
from app.api_v1 import routes_causas

# Inicializa la aplicación FastAPI
app = FastAPI(
    title="API de Riesgo de Devoluciones (Amazon)",
    description="Sirve los KPIs pre-calculados por el pipeline de Big Data (Spark).",
    version="1.0.0"
)

# "Monta" el router que creamos.
# Todas las rutas en 'routes_causas' ahora estarán bajo el prefijo /api/v1
app.include_router(routes_causas.router, prefix="/api/v1")

@app.get("/", tags=["Health"])
def read_root():
    """
    Endpoint raíz para verificar que la API está funcionando.
    """
    return {"status": "ok", "message": "API de Riesgo de Devoluciones V1"}