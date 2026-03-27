"""
Database connection for Taskly.
Connects to MongoDB Atlas via PyMongo.
"""
from pymongo import MongoClient

_client = None
_db = None

def init_db(uri: str = "mongodb+srv://localhost/taskly"):
    global _client, _db
    _client = MongoClient(uri)
    _db = _client["taskly"]

def get_db():
    return _db
