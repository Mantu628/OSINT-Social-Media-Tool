# Installation Guide for OSINT Social Media Tool

## System Requirements

- **Operating System**: Windows, macOS, or Linux
- **Python**: 3.8 or higher
- **Node.js**: 14.0 or higher (for web interface)
- **RAM**: Minimum 2GB (4GB recommended)
- **Disk Space**: At least 1GB for installation and dependencies
- **Internet**: Required for API calls and scraping

## Installation Methods

### Method 1: Web Application (Recommended)

#### Prerequisites
```bash
python --version  # Should be 3.8+
node --version    # Should be 14.0+
```

#### Step 1: Clone Repository
```bash
git clone https://github.com/Mantu628/OSINT-Social-Media-Tool.git
cd OSINT-Social-Media-Tool
```

#### Step 2: Create Virtual Environment
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### Step 3: Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### Step 4: Setup Web Frontend (Optional)
```bash
cd web
npm install
npm run build  # For production build
cd ..
```

#### Step 5: Configure Application
```bash
# Copy example environment file
cp .env.example .env

# Edit configuration
nano .env  # or use your favorite editor
```

#### Step 6: Initialize Database
```bash
python -c "from core.database import init_db; init_db()"
```

#### Step 7: Run Application
```bash
python app.py
```

Access the application at: `http://localhost:5000`

---

### Method 2: Command Line Interface (CLI)

#### Prerequisites
```bash
python --version  # Should be 3.8+
```

#### Step 1: Clone Repository
```bash
git clone https://github.com/Mantu628/OSINT-Social-Media-Tool.git
cd OSINT-Social-Media-Tool
```

#### Step 2: Create Virtual Environment
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 4: Make CLI Executable (macOS/Linux)
```bash
chmod +x cli.py
```

#### Step 5: Test Installation
```bash
python cli.py --help
```

#### Step 6: Start Using
```bash
# Basic search
python cli.py search --username john_doe --platforms twitter

# Email lookup
python cli.py email-lookup --email user@example.com

# Generate report
python cli.py report --username john_doe --platform twitter --format pdf
```

---

### Method 3: Desktop Application

#### Prerequisites
- Python 3.8+
- PyQt5 or PySimpleGUI
- All dependencies from requirements.txt

#### Installation Steps
```bash
# Clone repository
git clone https://github.com/Mantu628/OSINT-Social-Media-Tool.git
cd OSINT-Social-Media-Tool

# Create virtual environment
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install PyQt5==5.15.9

# Run desktop app
python desktop_app.py
```

---

## Configuration

### 1. Environment Variables (.env)

Create a `.env` file from the template:

```bash
cp .env.example .env
```

Edit configuration:

```ini
FLASK_ENV=development
SERVER_PORT=5000
DATABASE_URL=sqlite:///data/osint.db
REQUIRE_API_KEY=false
```

### 2. Configuration File (config.yaml)

Edit `config.yaml` for detailed settings:

```yaml
server:
  host: 127.0.0.1
  port: 5000
  debug: false

platforms:
  twitter:
    enabled: true
  instagram:
    enabled: true
```

### 3. API Keys (Optional)

Add your API keys to `.env`:

```ini
TWITTER_API_KEY=your_key_here
INSTAGRAM_ACCESS_TOKEN=your_token_here
GOOGLE_API_KEY=your_api_key_here
```

---

## Verification

### Test Web Application
```bash
python app.py
# Visit http://localhost:5000 in browser
# Should see the OSINT tool interface
```

### Test CLI
```bash
python cli.py --version
# Should display version 1.0.0

python cli.py search --help
# Should display help information
```

### Test API
```bash
curl http://localhost:5000/api/health
# Should return: {"status":"healthy",...}
```

---

## Troubleshooting

### Issue: Python not found
```bash
# Solution: Install Python 3.8+
# Windows: Download from python.org
# macOS: brew install python3
# Linux: apt-get install python3
```

### Issue: pip install fails
```bash
# Solution: Update pip
python -m pip install --upgrade pip

# Or use Python 3.8+ pip
pip install --upgrade pip setuptools wheel
```

### Issue: Port 5000 already in use
```bash
# Solution: Change port in .env
SERVER_PORT=5001

# Or kill process using port
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -i :5000
kill -9 <PID>
```

### Issue: Module not found error
```bash
# Solution: Ensure virtual environment is activated
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue: Database error
```bash
# Solution: Reinitialize database
rm data/osint.db  # Remove existing database
python -c "from core.database import init_db; init_db()"
```

---

## Security Setup

### 1. Change Secret Key
```bash
# Generate a new secret key
python -c "import secrets; print(secrets.token_hex(32))"

# Add to .env
SECRET_KEY=<generated_key>
```

### 2. Enable API Key Authentication
```yaml
# In config.yaml
security:
  require_api_key: true
  api_key_header: "X-API-Key"
```

### 3. Set Strong CORS Origins
```yaml
# In config.yaml
security:
  cors_origins:
    - "https://yourdomain.com"
    - "https://app.yourdomain.com"
```

### 4. Enable SSL/TLS
```python
# For production, use HTTPS
# Configure in nginx or Apache reverse proxy
```

---

## Docker Installation (Optional)

### Build Docker Image
```bash
docker build -t osint-tool .
```

### Run Docker Container
```bash
docker run -p 5000:5000 -v $(pwd)/data:/app/data osint-tool
```

---

## Updating

### Update from Git
```bash
# Pull latest changes
git pull origin main

# Activate virtual environment
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Update dependencies
pip install -r requirements.txt --upgrade
```

---

## Uninstallation

### Remove Application
```bash
# Deactivate virtual environment
deactivate

# Remove project directory
rm -rf OSINT-Social-Media-Tool

# Or on Windows
rmdir /s OSINT-Social-Media-Tool
```

---

## Support

If you encounter issues:

1. Check [FAQ.md](docs/FAQ.md)
2. Review [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
3. Open an [Issue on GitHub](https://github.com/Mantu628/OSINT-Social-Media-Tool/issues)
4. Check logs in `logs/` directory

---

## Next Steps

After installation:

1. Read the [README.md](README.md) for overview
2. Check [USAGE.md](docs/USAGE.md) for usage guide
3. Review [API.md](docs/API.md) for API documentation
4. Configure settings in `config.yaml`
5. Add API keys if using integrated services

Enjoy using the OSINT Social Media Tool! 🔍
