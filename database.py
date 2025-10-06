from motor.motor_asyncio import AsyncIOMotorClient
from config import settings

class Database:
    client: AsyncIOMotorClient = None
    
    @classmethod
    async def connect_db(cls):
        """Conectar a MongoDB"""
        cls.client = AsyncIOMotorClient(settings.MONGODB_URI)
        print(f"Conectado a MongoDB: {settings.DATABASE_NAME}")
    
    @classmethod
    async def close_db(cls):
        """Cerrar conexión a MongoDB"""
        if cls.client:
            cls.client.close()
            print("Conexión a MongoDB cerrada")
    
    @classmethod
    def get_db(cls):
        """Obtener la base de datos"""
        return cls.client[settings.DATABASE_NAME]

# Función auxiliar para obtener la base de datos
async def get_database():
    return Database.get_db()
