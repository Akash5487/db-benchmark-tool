#!/usr/bin/env python3
"""
Database Performance Benchmarking Tool
Main orchestrator for running benchmarks across multiple databases
"""

import yaml
import json
import time
import random
import argparse
from datetime import datetime
from typing import Dict, List, Any
from colorama import Fore, Style, init
from databases import PostgreSQLClient, MySQLClient, MongoDBClient

# Initialize colorama for colored terminal output
init(autoreset=True)

class BenchmarkOrchestrator:
    def __init__(self, config_path: str = 'config.yaml'):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'config': self.config['benchmark'],
            'databases': {}
        }
    
    def generate_test_data(self, size: int) -> Dict[str, List[tuple]]:
        """Generate synthetic test data"""
        print(f"\n{Fore.CYAN}Generating {size} test records...{Style.RESET_ALL}")
        
        cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose']
        categories = ['Electronics', 'Clothing', 'Books', 'Home & Garden', 'Sports', 'Toys', 'Food', 'Health', 'Beauty', 'Automotive']
        
        # Generate customers
        customers = [
            (f"Customer_{i}", f"customer{i}@email.com", random.choice(cities))
            for i in range(size)
        ]
        
        # Generate products
        products = [
            (f"Product_{i}", random.choice(categories), round(random.uniform(10, 500), 2), random.randint(0, 1000))
            for i in range(size // 2)
        ]
        
        # Generate orders
        orders = [
            (
                random.randint(1, size),
                random.randint(1, size // 2),
                random.randint(1, 10),
                round(random.uniform(50, 1000), 2)
            )
            for i in range(size * 2)
        ]
        
        return {
            'customers': customers,
            'products': products,
            'orders': orders
        }
    
    def run_crud_benchmark(self, client, test_data: Dict[str, List[tuple]]) -> Dict[str, float]:
        """Run CRUD operation benchmarks"""
        results = {}
        
        print(f"  → Testing INSERT operations...")
        results['insert_customers'] = client.insert_batch('customers', test_data['customers'][:1000])
        results['insert_products'] = client.insert_batch('products', test_data['products'][:500])
        results['insert_orders'] = client.insert_batch('orders', test_data['orders'][:2000])
        
        print(f"  → Testing SELECT operations...")
        results['select_simple'] = client.select_simple(1000)
        
        try:
            if hasattr(client, 'select_with_join'):
                results['select_join'] = client.select_with_join()
            else:
                results['select_aggregation'] = client.select_with_aggregation()
        except Exception as e:
            print(f"    {Fore.YELLOW}Warning: Complex query failed - {e}{Style.RESET_ALL}")
            results['select_join'] = None
        
        print(f"  → Testing UPDATE operations...")
        results['update_batch'] = client.update_batch(500)
        
        print(f"  → Testing DELETE operations...")
        results['delete_batch'] = client.delete_batch(100)
        
        return results
    
    def run_index_benchmark(self, client) -> Dict[str, Any]:
        """Test index performance impact"""
        results = {}
        
        print(f"  → Testing query WITHOUT index...")
        time_without = client.select_with_join() if hasattr(client, 'select_with_join') else client.select_simple(1000)
        
        print(f"  → Creating indexes...")
        client.create_index('customers', 'city')
        client.create_index('orders', 'customer_id')
        
        print(f"  → Testing query WITH index...")
        time_with = client.select_with_join() if hasattr(client, 'select_with_join') else client.select_simple(1000)
        
        results['without_index'] = time_without
        results['with_index'] = time_with
        results['improvement_percent'] = ((time_without - time_with) / time_without * 100) if time_without > 0 else 0
        
        return results
    
    def benchmark_database(self, db_name: str, client_class, config: Dict[str, Any]):
        """Run complete benchmark suite for a database"""
        print(f"\n{Fore.GREEN}{'='*60}")
        print(f"Benchmarking: {db_name.upper()}")
        print(f"{'='*60}{Style.RESET_ALL}\n")
        
        client = client_class(config)
        db_results = {}
        
        try:
            # Connect
            client.connect()
            time.sleep(1)
            
            # Setup schema
            print(f"{Fore.CYAN}Setting up schema...{Style.RESET_ALL}")
            client.setup_schema()
            
            # Generate test data
            test_data = self.generate_test_data(self.config['benchmark']['dataset_size'])
            
            # Run CRUD benchmarks
            print(f"\n{Fore.CYAN}Running CRUD benchmarks...{Style.RESET_ALL}")
            db_results['crud'] = self.run_crud_benchmark(client, test_data)
            
            # Run index benchmarks
            print(f"\n{Fore.CYAN}Running index impact tests...{Style.RESET_ALL}")
            db_results['indexing'] = self.run_index_benchmark(client)
            
            # Get final stats
            db_results['stats'] = {
                'customers_count': client.get_table_size('customers'),
                'products_count': client.get_table_size('products'),
                'orders_count': client.get_table_size('orders')
            }
            
            print(f"\n{Fore.GREEN}✓ {db_name.upper()} benchmark completed!{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"\n{Fore.RED}✗ {db_name.upper()} benchmark failed: {e}{Style.RESET_ALL}")
            db_results['error'] = str(e)
        
        finally:
            client.disconnect()
        
        return db_results
    
    def run_all_benchmarks(self):
        """Run benchmarks for all configured databases"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"DATABASE PERFORMANCE BENCHMARK TOOL")
        print(f"{'='*60}{Style.RESET_ALL}")
        print(f"Dataset size: {self.config['benchmark']['dataset_size']} records")
        print(f"Timestamp: {self.results['timestamp']}")
        
        # PostgreSQL
        self.results['databases']['postgresql'] = self.benchmark_database(
            'PostgreSQL',
            PostgreSQLClient,
            self.config['databases']['postgres']
        )
        
        # MySQL
        self.results['databases']['mysql'] = self.benchmark_database(
            'MySQL',
            MySQLClient,
            self.config['databases']['mysql']
        )
        
        # MongoDB
        self.results['databases']['mongodb'] = self.benchmark_database(
            'MongoDB',
            MongoDBClient,
            self.config['databases']['mongodb']
        )
        
        # Save results
        self.save_results()
        self.print_summary()
    
    def save_results(self):
        """Save benchmark results to JSON file"""
        import os
        os.makedirs('results', exist_ok=True)
        
        output_path = self.config['output']['json_results']
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n{Fore.GREEN}Results saved to: {output_path}{Style.RESET_ALL}")
    
    def print_summary(self):
        """Print benchmark summary"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"BENCHMARK SUMMARY")
        print(f"{'='*60}{Style.RESET_ALL}\n")
        
        for db_name, db_results in self.results['databases'].items():
            if 'error' in db_results:
                print(f"{Fore.RED}{db_name.upper()}: Failed - {db_results['error']}{Style.RESET_ALL}")
                continue
            
            print(f"{Fore.GREEN}{db_name.upper()}:{Style.RESET_ALL}")
            crud = db_results.get('crud', {})
            
            if crud:
                print(f"  Insert (1000 customers): {crud.get('insert_customers', 0)*1000:.2f}ms")
                print(f"  Select (simple):         {crud.get('select_simple', 0)*1000:.2f}ms")
                join_time = crud.get('select_join') or crud.get('select_aggregation')
                if join_time:
                    print(f"  Select (complex):        {join_time*1000:.2f}ms")
                print(f"  Update (500 rows):       {crud.get('update_batch', 0)*1000:.2f}ms")
                print(f"  Delete (100 rows):       {crud.get('delete_batch', 0)*1000:.2f}ms")
            
            indexing = db_results.get('indexing', {})
            if indexing:
                print(f"  Index improvement:       {indexing.get('improvement_percent', 0):.1f}%")
            
            print()

def main():
    parser = argparse.ArgumentParser(description='Database Performance Benchmarking Tool')
    parser.add_argument('--config', default='config.yaml', help='Path to configuration file')
    parser.add_argument('--all', action='store_true', help='Run all benchmarks')
    
    args = parser.parse_args()
    
    orchestrator = BenchmarkOrchestrator(args.config)
    orchestrator.run_all_benchmarks()

if __name__ == '__main__':
    main()
