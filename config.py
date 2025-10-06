import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Settings:
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017/MervalDB")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "MervalDB")
    DB_PORT: int = int(os.getenv("DB_PORT", "27017"))

settings = Settings()
