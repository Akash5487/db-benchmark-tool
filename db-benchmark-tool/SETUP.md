# Quick Setup Guide

## Prerequisites
- Docker Desktop installed and running
- Python 3.9 or higher
- Git

## Installation Steps

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/db-benchmark-tool.git
cd db-benchmark-tool
```

### 2. Create Virtual Environment (Recommended)
```bash
# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Start Database Containers
```bash
docker-compose up -d
```

Wait 10-15 seconds for databases to fully initialize.

### 5. Verify Databases are Running
```bash
docker-compose ps
```

You should see three containers running: `benchmark_postgres`, `benchmark_mysql`, and `benchmark_mongo`.

### 6. Run the Benchmark
```bash
python benchmark.py --all
```

This will:
- Create test schemas in all databases
- Generate synthetic data
- Run CRUD operation tests
- Test indexing performance
- Save results to `results/benchmark_results.json`

### 7. Generate HTML Report
```bash
python generate_report.py
```

Open `reports/index.html` in your browser to view the interactive report!

## Troubleshooting

### Docker Issues
**Problem**: Containers won't start
```bash
# Check Docker is running
docker --version

# Remove existing containers
docker-compose down -v

# Restart containers
docker-compose up -d
```

### Connection Issues
**Problem**: Cannot connect to database
```bash
# Check container logs
docker logs benchmark_postgres
docker logs benchmark_mysql
docker logs benchmark_mongo

# Ensure ports are not in use
netstat -an | grep 5432  # PostgreSQL
netstat -an | grep 3306  # MySQL
netstat -an | grep 27017 # MongoDB
```

### Python Package Issues
```bash
# Upgrade pip
pip install --upgrade pip

# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

## Customization

Edit `config.yaml` to adjust:
- Dataset size
- Number of iterations
- Concurrent connections
- Output paths

## Stopping the Environment

```bash
# Stop containers (keeps data)
docker-compose stop

# Stop and remove containers + data
docker-compose down -v
```

## Next Steps

- Read the full README.md
- Check CONTRIBUTING.md to add features
- Star the repo if you find it useful! ⭐
