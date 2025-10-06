# Sentiment Market API

API desarrollada con FastAPI para analizar y gestionar sentimientos de tweets relacionados con símbolos del mercado financiero.

## Características

- ✅ Conexión a MongoDB Atlas
- ✅ Análisis automático de sentimientos en tweets
- ✅ Asignación de sentimiento "desconocido" a tweets sin sentimiento
- ✅ Endpoints RESTful para gestión de datos
- ✅ Resumen de símbolos y sentimientos

## Requisitos

- Python 3.8+
- MongoDB Atlas o MongoDB local

## Instalación

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

2. Configurar variables de entorno en `.env` (ya configurado)

## Uso

### Iniciar el servidor

```bash
python main.py
```

O usando uvicorn directamente:
```bash
uvicorn main:app --reload
```

El servidor estará disponible en: `http://localhost:8000`

### Documentación interactiva

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Endpoints

### `GET /`
Información general de la API y lista de endpoints disponibles

### `GET /health`
Verifica el estado de la API y la conexión a la base de datos

### `POST /analyze-sentiments`
Analiza la colección de symbols y actualiza los sentimientos de los tweets:
- Si un tweet ya tiene sentimiento, lo mantiene
- Si no tiene sentimiento, le asigna "desconocido"

Respuesta:
```json
{
  "total_symbols": 10,
  "symbols_with_tweets": 8,
  "tweets_updated": 45,
  "tweets_with_sentiment": 20,
  "tweets_without_sentiment": 45,
  "message": "Análisis completado. 45 tweets actualizados con sentimiento 'desconocido'."
}
```

### `POST /create-sentiment-collection` ⭐ NUEVO
Crea o actualiza la colección `symbols_sentiment` con el sentimiento agregado de cada símbolo.

**Lógica de análisis:**
- Analiza todos los tweets de cada símbolo
- Determina el sentimiento general basado en la distribución:
  - **positivo**: Si más del 60% son positivos o es el sentimiento predominante
  - **negativo**: Si más del 60% son negativos o es el sentimiento predominante
  - **neutral**: Si no hay tweets o no hay sentimientos definidos
  - **mixto**: Si hay una mezcla equilibrada de positivos y negativos
- Calcula un score de confianza (0-1) basado en:
  - Proporción de tweets con sentimiento conocido
  - Concentración del sentimiento predominante

Respuesta:
```json
{
  "total_symbols_processed": 10,
  "symbols_created": 10,
  "symbols_with_positive": 4,
  "symbols_with_negative": 2,
  "symbols_with_neutral": 3,
  "symbols_with_mixed": 1,
  "message": "Colección 'symbols_sentiment' creada/actualizada exitosamente con 10 símbolos."
}
```

### `GET /symbols-sentiment` ⭐ NUEVO
Obtiene todos los sentimientos agregados de símbolos desde la colección `symbols_sentiment`.

Respuesta:
```json
{
  "total_symbols": 10,
  "symbols": [
    {
      "symbol": "AAPL",
      "sector": "Technology",
      "overall_sentiment": "positivo",
      "sentiment_counts": {
        "positivo": 12,
        "negativo": 2,
        "neutral": 1
      },
      "total_tweets": 15,
      "confidence_score": 0.85,
      "last_updated": "2025-10-06T12:30:00Z"
    },
    {
      "symbol": "TSLA",
      "sector": "Automotive",
      "overall_sentiment": "neutral",
      "sentiment_counts": {
        "neutral": 1
      },
      "total_tweets": 0,
      "confidence_score": 0.0,
      "last_updated": "2025-10-06T12:30:00Z"
    }
  ]
}
```

### `GET /symbols-summary`
Obtiene un resumen detallado de todos los símbolos con información sobre sus tweets y distribución de sentimientos

Respuesta:
```json
{
  "total_symbols": 10,
  "symbols": [
    {
      "symbol": "AAPL",
      "total_tweets": 15,
      "tweets_with_sentiment": 10,
      "tweets_without_sentiment": 5,
      "sentiments": {
        "positivo": 6,
        "negativo": 2,
        "neutral": 2,
        "desconocido": 5
      }
    }
  ]
}
```

## Estructura del Proyecto

```
SentimientoMercado/
├── main.py              # Aplicación FastAPI principal
├── config.py            # Configuración y variables de entorno
├── database.py          # Gestión de conexión a MongoDB
├── models.py            # Modelos Pydantic
├── services.py          # Lógica de negocio
├── requirements.txt     # Dependencias
├── .env                 # Variables de entorno
└── README.md           # Este archivo
```

## Base de Datos

La aplicación se conecta a MongoDB y trabaja con las siguientes colecciones:

### Colección `symbols`
Contiene los símbolos y sus tweets:

```json
{
  "_id": "ObjectId",
  "symbol": "AAPL",
  "tweets": [
    {
      "text": "Texto del tweet",
      "sentiment": "positivo",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Colección `symbols_sentiment` ⭐ NUEVA
Contiene el sentimiento agregado de cada símbolo:

```json
{
  "_id": "ObjectId",
  "symbol": "AAPL",
  "sector": "Technology",
  "overall_sentiment": "positivo",
  "sentiment_counts": {
    "positivo": 12,
    "negativo": 2,
    "neutral": 1
  },
  "total_tweets": 15,
  "confidence_score": 0.85,
  "last_updated": "2025-10-06T12:30:00Z"
}
```

**Campos:**
- `symbol`: Nombre del símbolo
- `sector`: Sector al que pertenece el símbolo (si está disponible)
- `overall_sentiment`: Sentimiento general calculado (positivo, negativo, neutral, mixto)
- `sentiment_counts`: Conteo de cada tipo de sentimiento encontrado en los tweets
- `total_tweets`: Total de tweets analizados
- `confidence_score`: Confianza del análisis (0-1), mayor valor = más confiable
- `last_updated`: Fecha y hora de última actualización

## Desarrollo

Para desarrollo, el servidor se recarga automáticamente al detectar cambios en el código.
