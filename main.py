from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from database import Database
from services import SentimentService
from models import SentimentResponse, CreateSentimentCollectionResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Conectar a la base de datos
    await Database.connect_db()
    yield
    # Shutdown: Cerrar conexión a la base de datos
    await Database.close_db()

# Crear la aplicación FastAPI
app = FastAPI(
    title="Sentiment Market API",
    description="API para análisis de sentimientos de tweets de símbolos del mercado",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "Sentiment Market API",
        "version": "1.0.0",
        "endpoints": {
            "/analyze-sentiments": "POST - Analiza y actualiza sentimientos de tweets",
            "/create-sentiment-collection": "POST - Crea/actualiza la colección symbols_sentiment",
            "/symbols-sentiment": "GET - Obtiene los sentimientos agregados de todos los símbolos",
            "/symbols-summary": "GET - Obtiene un resumen de símbolos y sentimientos",
            "/health": "GET - Verifica el estado de la API"
        }
    }

@app.get("/health")
async def health_check():
    """Verificar el estado de la API y la conexión a la base de datos"""
    try:
        db = await Database.get_db()
        # Intentar hacer un ping a la base de datos
        await db.command("ping")
        return {
            "status": "healthy",
            "database": "connected",
            "message": "API y base de datos funcionando correctamente"
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Error de conexión a la base de datos: {str(e)}"
        )

@app.post("/analyze-sentiments", response_model=SentimentResponse)
async def analyze_sentiments():
    """
    Analiza la colección de symbols y asigna sentimientos a los tweets.
    - Si el tweet ya tiene sentimiento, lo mantiene.
    - Si no tiene sentimiento, le asigna 'desconocido'.
    """
    try:
        result = await SentimentService.analyze_and_update_sentiments()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al analizar sentimientos: {str(e)}"
        )

@app.post("/create-sentiment-collection", response_model=CreateSentimentCollectionResponse)
async def create_sentiment_collection():
    """
    Crea o actualiza la colección 'symbols_sentiment' con el sentimiento agregado de cada símbolo.
    
    Analiza todos los tweets de cada símbolo y determina el sentimiento general:
    - 'positivo': Si predominan tweets positivos
    - 'negativo': Si predominan tweets negativos
    - 'neutral': Si no hay tweets o no hay sentimiento definido
    - 'mixto': Si hay una mezcla equilibrada de sentimientos
    
    Incluye:
    - overall_sentiment: Sentimiento general del símbolo
    - sentiment_counts: Conteo de cada tipo de sentimiento
    - total_tweets: Total de tweets analizados
    - confidence_score: Score de confianza (0-1) basado en cantidad y distribución
    - last_updated: Fecha de última actualización
    """
    try:
        result = await SentimentService.create_symbols_sentiment_collection()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear colección de sentimientos: {str(e)}"
        )

@app.get("/symbols-sentiment")
async def get_symbols_sentiment():
    """
    Obtiene todos los sentimientos agregados de símbolos desde la colección 'symbols_sentiment'.
    
    Retorna información detallada incluyendo:
    - symbol: Nombre del símbolo
    - overall_sentiment: Sentimiento general (positivo, negativo, neutral, mixto)
    - sentiment_counts: Distribución de sentimientos en los tweets
    - total_tweets: Cantidad de tweets analizados
    - confidence_score: Score de confianza del análisis
    - last_updated: Fecha de última actualización
    """
    try:
        result = await SentimentService.get_symbols_sentiment()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener sentimientos de símbolos: {str(e)}"
        )

@app.get("/symbols-summary")
async def get_symbols_summary():
    """
    Obtiene un resumen de todos los símbolos con información sobre sus tweets y sentimientos
    """
    try:
        summary = await SentimentService.get_symbols_summary()
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener resumen: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
