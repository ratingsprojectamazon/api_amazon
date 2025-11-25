# 🧠 Amazon Electronics Risk Service - API

Este directorio contiene el **Backend de Servicio** del sistema. Es una API RESTful de alto rendimiento construida con **FastAPI**, diseñada para desacoplar el procesamiento pesado (Big Data) de la capa de visualización.

Su función principal es actuar como una capa de servicio de baja latencia (Low Latency Serving Layer) que lee los resultados pre-calculados por el Pipeline de Spark (Zona Gold) y los entrega al Frontend.

## 🛠️ Stack Tecnológico

* **Framework Web:** `FastAPI` (v0.110+) - Elegido por su velocidad y validación automática de tipos.
* **Servidor:** `Uvicorn` - Servidor ASGI para producción.
* **Acceso a Datos:** `PyArrow` & `Pandas` - Para la lectura eficiente de archivos Parquet particionados.
* **Validación:** `Pydantic` - Definición estricta de esquemas de entrada/salida (Contracts).

---

## 🏗️ Arquitectura del Backend

El proyecto sigue una variante de **Clean Architecture** simplificada para microservicios de datos, separando responsabilidades en capas:

```text
app/
├── api_v1/       # CAPA DE CONTROLADORES (Rutas y Endpoints HTTP)
├── services/     # CAPA DE NEGOCIO (Transformación y lógica)
├── data_access/  # CAPA DE DATOS (Abstracción de lectura HDFS/Local)
├── models/       # CAPA DE DOMINIO (Schemas Pydantic)
└── core/         # CONFIGURACIÓN (Variables de entorno)
```
### Patrón de Acceso a Datos Híbrido
Esta es la característica técnica más relevante. El módulo `data_access/gold_reader.py` implementa una lógica de lectura agnóstica al entorno:

1.  **Modo Producción (HDFS):** Si se detecta la variable de entorno `USE_HDFS=True`, el sistema utiliza `pyarrow.fs.HadoopFileSystem` para conectarse directamente al NameNode del clúster y leer desde el Data Lake distribuido.
2.  **Modo Desarrollo (Snapshot Local):** Si no se detecta HDFS, el sistema hace un *fallback* automático para leer archivos Parquet desde el sistema de archivos local (`local_data/`). Esto permite desarrollar y demostrar la solución en equipos sin infraestructura Hadoop instalada.

---

## 🔌 Documentación de Endpoints

La API expone los siguientes recursos bajo el prefijo `/api/v1`. Puedes ver la documentación interactiva (Swagger UI) en `/docs` cuando el servicio está activo.

### 1. Ranking de Riesgo
Devuelve la lista de productos priorizados por su índice de riesgo y volumen de quejas.
* **Endpoint:** `GET /ranking/riesgo`
* **Parámetros:**
    * `periodo` (str): Mes a consultar (Formato: `YYYY-MM`).
    * `top_n` (int): Límite de resultados a retornar.
* **Respuesta:** JSON Array con metadatos del producto y métricas de riesgo pre-calculadas.

### 2. Mapa de Causas
Devuelve el desglose de causas raíz para un producto específico.
* **Endpoint:** `GET /productos/{asin}/mapa-causas`
* **Parámetros:** `asin` (str), `periodo` (str).
* **Respuesta:** Objeto JSON con contadores por categoría (ej. `no_funciona`, `baja_calidad`, `no_compatible`).

### 3. Evidencia Textual
Recupera fragmentos de texto originales para validación humana (Drill-down).
* **Endpoint:** `GET /productos/{asin}/evidencia`
* **Parámetros:** `asin`, `periodo`, `causa`.
* **Nota:** En el entorno local (Snapshot), este endpoint puede devolver una lista vacía si no se ha descargado la data masiva de la capa Silver.

---

## ⚙️ Instalación y Ejecución

### 1. Requisitos Previos
Asegúrate de estar dentro de la carpeta `backend_api_riesgo`.

```bash
# Crear entorno virtual (Recomendado)
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```
### 2. Configuración de Datos (Solo para modo Local)
Si vas a ejecutar sin HDFS, asegúrate de tener los resultados del ETL en la carpeta local:
```bash
backend_api_riesgo/local_data/gold/results/ranking_riesgo_mensual/

backend_api_riesgo/local_data/gold/results/mapa_causas_mensual/
```
### 3. Ejecución en Desarrollo (Local)
Este comando inicia el servidor con recarga automática (--reload).
```bash
uvicorn app.main:app --reload
```
- URL Base: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs