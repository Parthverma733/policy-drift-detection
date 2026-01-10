"""MongoDB database connection and utilities."""

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from typing import Optional
import os
from datetime import datetime
from bson import ObjectId
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class MongoDBClient:
    """MongoDB client wrapper for async operations."""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        self.connected = False
    
    async def connect(self, connection_string: Optional[str] = None):
        """Connect to MongoDB."""
        if connection_string is None:
            connection_string = os.getenv(
                "MONGODB_URI",
                "mongodb+srv://gaurav2921singh_db_user:0LWiCzxExxUU4BC3@policydrift.slmbmvv.mongodb.net/"
            )
        
        try:
            self.client = AsyncIOMotorClient(
                connection_string,
                serverSelectionTimeoutMS=5000
            )
            await self.client.admin.command('ping')
            db_name = os.getenv("MONGODB_DB", "policylens")
            self.db = self.client[db_name]
            self.connected = True
            return True
        except ConnectionFailure:
            self.connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from MongoDB."""
        if self.client:
            self.client.close()
            self.connected = False
    
    def get_collection(self, name: str):
        """Get a collection by name."""
        if not self.db:
            raise RuntimeError("Database not connected")
        return self.db[name]


# Global MongoDB client instance
mongodb_client = MongoDBClient()


async def get_db():
    """Get database instance."""
    if not mongodb_client.connected:
        await mongodb_client.connect()
    return mongodb_client.db


def object_id_to_str(obj):
    """Convert ObjectId to string in a dict."""
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: object_id_to_str(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [object_id_to_str(item) for item in obj]
    return obj
