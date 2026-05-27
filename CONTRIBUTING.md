# Contributing to OSINT Social Media Tool

## Code of Conduct

This project is committed to providing a welcoming and inspiring community for all.

## How to Contribute

### Reporting Issues
- Check if the issue already exists
- Provide detailed description
- Include steps to reproduce
- Attach relevant logs or screenshots

### Pull Requests
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/OSINT-Social-Media-Tool.git
cd OSINT-Social-Media-Tool

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt

# Run tests
pytest

# Format code
black .

# Run linter
flake8 .
```

## Testing

```bash
# Run all tests
pytest

# Run specific test
pytest tests/test_utils.py

# Run with coverage
pytest --cov=osint_tool
```

## Code Style

- Follow PEP 8
- Use type hints
- Write docstrings for all functions
- Use meaningful variable names
- Keep functions focused and small

## Commit Messages

- Use clear and descriptive messages
- Start with an action verb (Add, Fix, Update, etc.)
- Reference issues when applicable

## Areas for Contribution

- [ ] Add new platform support
- [ ] Improve data extraction methods
- [ ] Enhanced analysis features
- [ ] Better error handling
- [ ] Documentation improvements
- [ ] Performance optimization
- [ ] Security improvements

Thank you for contributing!
