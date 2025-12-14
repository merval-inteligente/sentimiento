from database import get_database, Database
from typing import Dict, List
from datetime import datetime

class SentimentService:
    """Servicio para análisis de sentimientos"""
    
    @staticmethod
    async def analyze_and_update_sentiments() -> Dict:
        """
        Analiza la colección symbols y asigna sentimientos a los tweets.
        Si el tweet tiene sentimiento, lo mantiene.
        Si no tiene sentimiento, le asigna 'desconocido'.
        """
        db = Database.get_db()
        symbols_collection = db["symbols"]
        
        # Obtener todos los símbolos
        symbols = await symbols_collection.find({}).to_list(length=None)
        
        total_symbols = len(symbols)
        symbols_with_tweets = 0
        tweets_updated = 0
        tweets_with_sentiment = 0
        tweets_without_sentiment = 0
        
        for symbol in symbols:
            if "tweets" in symbol and symbol["tweets"]:
                symbols_with_tweets += 1
                
                # Procesar cada tweet
                updated_tweets = []
                for tweet in symbol["tweets"]:
                    # Verificar si el tweet tiene sentimiento
                    if "sentiment" in tweet and tweet["sentiment"]:
                        # Ya tiene sentimiento, mantenerlo
                        tweets_with_sentiment += 1
                        updated_tweets.append(tweet)
                    else:
                        # No tiene sentimiento, asignar 'desconocido'
                        tweet["sentiment"] = "desconocido"
                        tweets_without_sentiment += 1
                        tweets_updated += 1
                        updated_tweets.append(tweet)
                
                # Actualizar el documento en la base de datos
                if tweets_updated > 0:
                    await symbols_collection.update_one(
                        {"_id": symbol["_id"]},
                        {"$set": {"tweets": updated_tweets}}
                    )
        
        return {
            "total_symbols": total_symbols,
            "symbols_with_tweets": symbols_with_tweets,
            "tweets_updated": tweets_updated,
            "tweets_with_sentiment": tweets_with_sentiment,
            "tweets_without_sentiment": tweets_without_sentiment,
            "message": f"Análisis completado. {tweets_updated} tweets actualizados con sentimiento 'desconocido'."
        }
    
    @staticmethod
    def _normalize_sentiment(sentiment: str, sentiment_prob: dict = None) -> str:
        """
        Normaliza los diferentes formatos de sentimiento a un formato estándar.
        Si sentiment está vacío pero hay sentiment_prob, usa la probabilidad más alta.
        """
        # Si no hay sentimiento pero hay probabilidades, usar la más alta
        if (not sentiment or sentiment == "") and sentiment_prob:
            max_prob = 0
            max_sentiment = "neutral"
            for sent_key, prob in sentiment_prob.items():
                if prob > max_prob:
                    max_prob = prob
                    max_sentiment = sent_key
            sentiment = max_sentiment
        
        if not sentiment:
            return "neutral"
        
        sentiment = sentiment.lower().strip()
        
        # Mapeo de sentimientos
        sentiment_map = {
            "pos": "positivo",
            "positive": "positivo",
            "positivo": "positivo",
            "neg": "negativo",
            "negative": "negativo",
            "negativo": "negativo",
            "neu": "neutral",
            "neutral": "neutral",
            "neutro": "neutral",
            "desconocido": "desconocido"
        }
        
        return sentiment_map.get(sentiment, "neutral")
    
    @staticmethod
    def _calculate_overall_sentiment(sentiment_counts: Dict[str, int]) -> str:
        """
        Calcula el sentimiento general basado en el conteo de sentimientos.
        
        Reglas:
        - Si no hay tweets o todos son desconocidos -> neutral
        - Si positivo > negativo y positivo > neutral -> positivo
        - Si negativo > positivo y negativo > neutral -> negativo
        - Si hay mezcla equilibrada -> mixto
        - Por defecto -> neutral
        """
        if not sentiment_counts:
            return "neutral"
        
        # Remover 'desconocido' del análisis
        known_sentiments = {k: v for k, v in sentiment_counts.items() if k != "desconocido"}
        
        if not known_sentiments:
            return "neutral"
        
        positive = known_sentiments.get("positivo", 0)
        negative = known_sentiments.get("negativo", 0)
        neutral = known_sentiments.get("neutral", 0)
        
        total = positive + negative + neutral
        
        if total == 0:
            return "neutral"
        
        # Calcular porcentajes
        positive_pct = positive / total
        negative_pct = negative / total
        
        # Si hay más de 60% de un sentimiento, ese predomina
        if positive_pct > 0.6:
            return "positivo"
        elif negative_pct > 0.6:
            return "negativo"
        elif positive_pct > 0.4 and negative_pct > 0.4:
            return "mixto"
        elif positive > negative and positive > neutral:
            return "positivo"
        elif negative > positive and negative > neutral:
            return "negativo"
        else:
            return "neutral"
    
    @staticmethod
    def _calculate_confidence_score(sentiment_counts: Dict[str, int], total_tweets: int) -> float:
        """
        Calcula un score de confianza basado en la cantidad y distribución de sentimientos.
        Retorna un valor entre 0 y 1.
        """
        if total_tweets == 0:
            return 0.0
        
        # Remover 'desconocido' del análisis
        known_sentiments = {k: v for k, v in sentiment_counts.items() if k != "desconocido"}
        known_count = sum(known_sentiments.values())
        
        if known_count == 0:
            return 0.0
        
        # Factor 1: Proporción de tweets con sentimiento conocido
        known_ratio = known_count / total_tweets
        
        # Factor 2: Concentración del sentimiento (qué tan dominante es el sentimiento principal)
        if known_sentiments:
            max_sentiment = max(known_sentiments.values())
            concentration = max_sentiment / known_count
        else:
            concentration = 0
        
        # Combinar factores
        confidence = (known_ratio * 0.6) + (concentration * 0.4)
        
        return round(confidence, 2)
    
    @staticmethod
    async def create_symbols_sentiment_collection() -> Dict:
        """
        Crea/actualiza la colección symbols_sentiment con el sentimiento agregado de cada símbolo.
        Lee los tweets desde la colección 'tweets' y los agrupa por el campo 'company'.
        """
        db = Database.get_db()
        symbols_collection = db["symbols"]
        tweets_collection = db["tweets"]
        sentiment_collection = db["symbols_sentiment"]
        
        # Obtener todos los símbolos
        symbols = await symbols_collection.find({}).to_list(length=None)
        
        total_symbols_processed = 0
        symbols_created = 0
        sentiment_stats = {
            "positivo": 0,
            "negativo": 0,
            "neutral": 0,
            "mixto": 0
        }
        
        for symbol in symbols:
            total_symbols_processed += 1
            symbol_name = symbol.get("symbol", "Unknown")
            symbol_sector = symbol.get("sector", None)
            
            # Buscar tweets del símbolo en la colección tweets
            tweets = await tweets_collection.find({"company": symbol_name}).to_list(length=None)
            
            # Analizar tweets del símbolo
            sentiment_counts = {}
            total_tweets = len(tweets)
            
            if tweets:
                for tweet in tweets:
                    raw_sentiment = tweet.get("sentiment", "")
                    sentiment_prob = tweet.get("sentiment_prob", None)
                    
                    # Normalizar el sentimiento usando la función de normalización
                    # Si sentiment está vacío, usará sentiment_prob
                    sentiment = SentimentService._normalize_sentiment(raw_sentiment, sentiment_prob)
                    
                    if sentiment in sentiment_counts:
                        sentiment_counts[sentiment] += 1
                    else:
                        sentiment_counts[sentiment] = 1
            
            # Si no hay tweets, asignar neutral
            if total_tweets == 0:
                overall_sentiment = "neutral"
                sentiment_counts = {"neutral": 1}
                sentiment_percentages = {"neutral": 0.0}
                confidence_score = 0.0
            else:
                # Calcular sentimiento general
                overall_sentiment = SentimentService._calculate_overall_sentiment(sentiment_counts)
                confidence_score = SentimentService._calculate_confidence_score(sentiment_counts, total_tweets)
                
                # Calcular porcentajes
                sentiment_percentages = {}
                for sent, count in sentiment_counts.items():
                    percentage = round((count / total_tweets) * 100, 2)
                    sentiment_percentages[sent] = percentage
            
            # Actualizar estadísticas
            sentiment_stats[overall_sentiment] = sentiment_stats.get(overall_sentiment, 0) + 1
            
            # Crear/actualizar documento en symbols_sentiment
            symbol_sentiment_doc = {
                "symbol": symbol_name,
                "sector": symbol_sector,
                "overall_sentiment": overall_sentiment,
                "sentiment_counts": sentiment_counts,
                "sentiment_percentages": sentiment_percentages,
                "total_tweets": total_tweets,
                "confidence_score": confidence_score,
                "last_updated": datetime.utcnow()
            }
            
            # Usar upsert para crear o actualizar
            await sentiment_collection.update_one(
                {"symbol": symbol_name},
                {"$set": symbol_sentiment_doc},
                upsert=True
            )
            symbols_created += 1
        
        return {
            "total_symbols_processed": total_symbols_processed,
            "symbols_created": symbols_created,
            "symbols_with_positive": sentiment_stats.get("positivo", 0),
            "symbols_with_negative": sentiment_stats.get("negativo", 0),
            "symbols_with_neutral": sentiment_stats.get("neutral", 0),
            "symbols_with_mixed": sentiment_stats.get("mixto", 0),
            "message": f"Colección 'symbols_sentiment' creada/actualizada exitosamente con {symbols_created} símbolos."
        }
    
    @staticmethod
    async def get_symbols_sentiment() -> Dict:
        """Obtiene todos los sentimientos de símbolos de la colección symbols_sentiment"""
        db = Database.get_db()
        sentiment_collection = db["symbols_sentiment"]
        
        # Obtener todos los documentos
        sentiments = await sentiment_collection.find({}).to_list(length=None)
        
        # Convertir ObjectId a string para serialización
        for sentiment in sentiments:
            if "_id" in sentiment:
                sentiment["_id"] = str(sentiment["_id"])
        
        return {
            "total_symbols": len(sentiments),
            "symbols": sentiments
        }
    
    @staticmethod
    async def get_symbols_summary() -> Dict:
        """Obtiene un resumen de los símbolos y sus tweets desde la colección tweets"""
        db = Database.get_db()
        symbols_collection = db["symbols"]
        tweets_collection = db["tweets"]
        
        # Obtener todos los símbolos
        symbols = await symbols_collection.find({}).to_list(length=None)
        
        summary = []
        for symbol in symbols:
            symbol_name = symbol.get("symbol", "Unknown")
            
            # Buscar tweets del símbolo
            tweets = await tweets_collection.find({"company": symbol_name}).to_list(length=None)
            
            symbol_data = {
                "symbol": symbol_name,
                "total_tweets": len(tweets),
                "tweets_with_sentiment": 0,
                "tweets_without_sentiment": 0,
                "sentiments": {}
            }
            
            # Analizar tweets
            for tweet in tweets:
                sentiment = tweet.get("sentiment", "")
                sentiment_prob = tweet.get("sentiment_prob", None)
                
                # Normalizar sentimiento
                normalized_sentiment = SentimentService._normalize_sentiment(sentiment, sentiment_prob)
                
                if sentiment or sentiment_prob:
                    symbol_data["tweets_with_sentiment"] += 1
                    if normalized_sentiment in symbol_data["sentiments"]:
                        symbol_data["sentiments"][normalized_sentiment] += 1
                    else:
                        symbol_data["sentiments"][normalized_sentiment] = 1
                else:
                    symbol_data["tweets_without_sentiment"] += 1
            
            summary.append(symbol_data)
        
        return {
            "total_symbols": len(summary),
            "symbols": summary
        }
