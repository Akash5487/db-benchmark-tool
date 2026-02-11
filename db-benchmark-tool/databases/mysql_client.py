import mysql.connector
from mysql.connector import Error
import time
from typing import List, Dict, Any

class MySQLClient:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """Establish connection to MySQL"""
        try:
            self.connection = mysql.connector.connect(
                host=self.config['host'],
                port=self.config['port'],
                user=self.config['user'],
                password=self.config['password'],
                database=self.config['database']
            )
            self.cursor = self.connection.cursor()
            print("✓ MySQL connected")
        except Error as e:
            print(f"✗ MySQL connection failed: {e}")
            raise
    
    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
    
    def setup_schema(self):
        """Create test tables"""
        self.cursor.execute("SET FOREIGN_KEY_CHECKS=0")
        self.cursor.execute("DROP TABLE IF EXISTS orders")
        self.cursor.execute("DROP TABLE IF EXISTS customers")
        self.cursor.execute("DROP TABLE IF EXISTS products")
        self.cursor.execute("SET FOREIGN_KEY_CHECKS=1")
        
        self.cursor.execute("""
            CREATE TABLE customers (
                customer_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                email VARCHAR(100),
                city VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.cursor.execute("""
            CREATE TABLE products (
                product_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                category VARCHAR(50),
                price DECIMAL(10, 2),
                stock INT
            )
        """)
        
        self.cursor.execute("""
            CREATE TABLE orders (
                order_id INT AUTO_INCREMENT PRIMARY KEY,
                customer_id INT,
                product_id INT,
                quantity INT,
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_amount DECIMAL(10, 2),
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            )
        """)
        
        self.connection.commit()
        print("✓ MySQL schema created")
    
    def insert_batch(self, table: str, data: List[tuple]) -> float:
        """Batch insert and return execution time"""
        start_time = time.time()
        
        if table == 'customers':
            query = "INSERT INTO customers (name, email, city) VALUES (%s, %s, %s)"
        elif table == 'products':
            query = "INSERT INTO products (name, category, price, stock) VALUES (%s, %s, %s, %s)"
        elif table == 'orders':
            query = "INSERT INTO orders (customer_id, product_id, quantity, total_amount) VALUES (%s, %s, %s, %s)"
        
        self.cursor.executemany(query, data)
        self.connection.commit()
        
        return time.time() - start_time
    
    def select_simple(self, limit: int = 1000) -> float:
        """Simple SELECT query"""
        start_time = time.time()
        self.cursor.execute(f"SELECT * FROM customers LIMIT {limit}")
        results = self.cursor.fetchall()
        return time.time() - start_time
    
    def select_with_join(self) -> float:
        """Complex JOIN query"""
        start_time = time.time()
        self.cursor.execute("""
            SELECT c.name, c.city, p.name as product, o.quantity, o.total_amount
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            JOIN products p ON o.product_id = p.product_id
            WHERE o.total_amount > 100
            ORDER BY o.order_date DESC
            LIMIT 1000
        """)
        results = self.cursor.fetchall()
        return time.time() - start_time
    
    def update_batch(self, limit: int = 1000) -> float:
        """Batch update operation"""
        start_time = time.time()
        self.cursor.execute(f"""
            UPDATE products 
            SET stock = stock - 1 
            WHERE product_id IN (SELECT product_id FROM (SELECT product_id FROM products LIMIT {limit}) AS temp)
        """)
        self.connection.commit()
        return time.time() - start_time
    
    def delete_batch(self, limit: int = 100) -> float:
        """Batch delete operation"""
        start_time = time.time()
        self.cursor.execute(f"""
            DELETE FROM orders 
            WHERE order_id IN (SELECT order_id FROM (SELECT order_id FROM orders LIMIT {limit}) AS temp)
        """)
        self.connection.commit()
        return time.time() - start_time
    
    def create_index(self, table: str, column: str):
        """Create index on specified column"""
        index_name = f"idx_{table}_{column}"
        try:
            self.cursor.execute(f"CREATE INDEX {index_name} ON {table}({column})")
            self.connection.commit()
        except Error:
            pass  # Index might already exist
    
    def drop_index(self, table: str, column: str):
        """Drop index from specified column"""
        index_name = f"idx_{table}_{column}"
        try:
            self.cursor.execute(f"DROP INDEX {index_name} ON {table}")
            self.connection.commit()
        except Error:
            pass  # Index might not exist
    
    def get_table_size(self, table: str) -> int:
        """Get number of rows in table"""
        self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
        return self.cursor.fetchone()[0]
