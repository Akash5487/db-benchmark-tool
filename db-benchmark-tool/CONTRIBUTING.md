# Contributing to Database Benchmark Tool

Thank you for your interest in contributing! 🎉

## How to Contribute

### Reporting Bugs
- Use GitHub Issues
- Include system info (OS, Python version, database versions)
- Provide steps to reproduce
- Include error messages and logs

### Suggesting Features
- Open an issue with the "enhancement" label
- Describe the use case
- Explain expected behavior

### Code Contributions

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow PEP 8 style guide
   - Add docstrings to functions
   - Update README if needed

4. **Test your changes**
   ```bash
   python benchmark.py --all
   ```

5. **Commit with clear messages**
   ```bash
   git commit -m "Add feature: your feature description"
   ```

6. **Push and create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/db-benchmark-tool.git
cd db-benchmark-tool

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start databases
docker-compose up -d
```

## Adding New Database Support

1. Create new client class in `databases/`
2. Implement required methods (connect, disconnect, setup_schema, insert_batch, etc.)
3. Update `benchmark.py` to include new database
4. Update documentation

## Code Style
- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use type hints where appropriate
- Document complex logic

## Questions?
Open an issue or reach out to the maintainers!
