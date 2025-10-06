from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime

class Tweet(BaseModel):
    """Modelo para un tweet"""
    text: Optional[str] = None
    sentiment: Optional[str] = None
    created_at: Optional[datetime] = None
    
class Symbol(BaseModel):
    """Modelo para un símbolo"""
    symbol: str
    tweets: Optional[List[Tweet]] = []
    
class SentimentUpdate(BaseModel):
    """Modelo para actualización de sentimiento"""
    matched_count: int
    modified_count: int
    
class SentimentResponse(BaseModel):
    """Respuesta del análisis de sentimientos"""
    total_symbols: int
    symbols_with_tweets: int
    tweets_updated: int
    tweets_with_sentiment: int
    tweets_without_sentiment: int
    message: str

class SymbolSentiment(BaseModel):
    """Modelo para el sentimiento de un símbolo"""
    symbol: str
    sector: Optional[str] = None
    overall_sentiment: str
    sentiment_counts: dict
    total_tweets: int
    confidence_score: Optional[float] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class CreateSentimentCollectionResponse(BaseModel):
    """Respuesta de la creación de la colección de sentimientos"""
    total_symbols_processed: int
    symbols_created: int
    symbols_with_positive: int
    symbols_with_negative: int
    symbols_with_neutral: int
    symbols_with_mixed: int
    message: str
