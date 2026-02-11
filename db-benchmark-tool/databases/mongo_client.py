from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import time
from typing import List, Dict, Any

class MongoDBClient:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = None
        self.db = None
    
    def connect(self):
        """Establish connection to MongoDB"""
        try:
            connection_string = f"mongodb://{self.config['user']}:{self.config['password']}@{self.config['host']}:{self.config['port']}"
            self.client = MongoClient(connection_string)
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[self.config['database']]
            print("✓ MongoDB connected")
        except ConnectionFailure as e:
            print(f"✗ MongoDB connection failed: {e}")
            raise
    
    def disconnect(self):
        """Close database connection"""
        if self.client:
            self.client.close()
    
    def setup_schema(self):
        """Create collections (MongoDB equivalent of tables)"""
        # Drop existing collections
        self.db.customers.drop()
        self.db.products.drop()
        self.db.orders.drop()
        
        # Collections are created automatically on first insert
        print("✓ MongoDB collections ready")
    
    def insert_batch(self, table: str, data: List[tuple]) -> float:
        """Batch insert and return execution time"""
        start_time = time.time()
        
        collection = self.db[table]
        
        if table == 'customers':
            documents = [
                {"name": row[0], "email": row[1], "city": row[2], "created_at": time.time()}
                for row in data
            ]
        elif table == 'products':
            documents = [
                {"name": row[0], "category": row[1], "price": float(row[2]), "stock": row[3]}
                for row in data
            ]
        elif table == 'orders':
            documents = [
                {
                    "customer_id": row[0], 
                    "product_id": row[1], 
                    "quantity": row[2], 
                    "total_amount": float(row[3]),
                    "order_date": time.time()
                }
                for row in data
            ]
        
        collection.insert_many(documents)
        return time.time() - start_time
    
    def select_simple(self, limit: int = 1000) -> float:
        """Simple SELECT query"""
        start_time = time.time()
        results = list(self.db.customers.find().limit(limit))
        return time.time() - start_time
    
    def select_with_aggregation(self) -> float:
        """Complex aggregation query (MongoDB doesn't have traditional joins)"""
        start_time = time.time()
        pipeline = [
            {
                "$lookup": {
                    "from": "customers",
                    "localField": "customer_id",
                    "foreignField": "_id",
                    "as": "customer_info"
                }
            },
            {
                "$lookup": {
                    "from": "products",
                    "localField": "product_id",
                    "foreignField": "_id",
                    "as": "product_info"
                }
            },
            {"$match": {"total_amount": {"$gt": 100}}},
            {"$sort": {"order_date": -1}},
            {"$limit": 1000}
        ]
        results = list(self.db.orders.aggregate(pipeline))
        return time.time() - start_time
    
    def update_batch(self, limit: int = 1000) -> float:
        """Batch update operation"""
        start_time = time.time()
        
        # Get first N product IDs
        product_ids = [doc['_id'] for doc in self.db.products.find().limit(limit)]
        
        # Update stock
        self.db.products.update_many(
            {"_id": {"$in": product_ids}},
            {"$inc": {"stock": -1}}
        )
        
        return time.time() - start_time
    
    def delete_batch(self, limit: int = 100) -> float:
        """Batch delete operation"""
        start_time = time.time()
        
        # Get first N order IDs
        order_ids = [doc['_id'] for doc in self.db.orders.find().limit(limit)]
        
        # Delete orders
        self.db.orders.delete_many({"_id": {"$in": order_ids}})
        
        return time.time() - start_time
    
    def create_index(self, table: str, column: str):
        """Create index on specified column"""
        collection = self.db[table]
        collection.create_index([(column, 1)])
    
    def drop_index(self, table: str, column: str):
        """Drop index from specified column"""
        collection = self.db[table]
        try:
            collection.drop_index(f"{column}_1")
        except:
            pass  # Index might not exist
    
    def get_table_size(self, table: str) -> int:
        """Get number of documents in collection"""
        return self.db[table].count_documents({})
