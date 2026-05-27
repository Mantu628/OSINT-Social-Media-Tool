"""
OSINT Social Media Tool - Web Application
Main Flask application for the web interface
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, jsonify, request, send_file, session
from flask_cors import CORS
from flask_restful import Api
from dotenv import load_dotenv
import yaml

# Load environment variables
load_dotenv()

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create Flask application
app = Flask(
    __name__,
    template_folder='web/build' if os.path.exists('web/build') else 'web/public',
    static_folder='web/build/static' if os.path.exists('web/build/static') else 'web/public/static'
)

# Load configuration
def load_config():
    """Load configuration from config.yaml"""
    config_path = PROJECT_ROOT / 'config.yaml'
    if config_path.exists():
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    return {}

config = load_config()

# Application Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SESSION_COOKIE_SECURE'] = os.getenv('SECURE_COOKIES', False)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour
app.config.update(config)

# Enable CORS
CORS(app, resources={
    r"/api/*": {
        "origins": config.get('security', {}).get('cors_origins', ["http://localhost:3000"]),
        "methods": config.get('security', {}).get('cors_methods', ["GET", "POST", "PUT", "DELETE"]),
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Initialize Flask-RESTful API
api = Api(app)

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)
os.makedirs('data', exist_ok=True)
os.makedirs('exports', exist_ok=True)

# ============================================================================
# Authentication & Authorization
# ============================================================================

def require_api_key(f):
    """Decorator to require API key for endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not config.get('security', {}).get('require_api_key'):
            return f(*args, **kwargs)
        
        api_key = request.headers.get(
            config.get('security', {}).get('api_key_header', 'X-API-Key')
        )
        
        if not api_key or not validate_api_key(api_key):
            return jsonify({
                'status': 'error',
                'message': 'Invalid or missing API key'
            }), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

def validate_api_key(api_key):
    """Validate API key (implement your own logic)"""
    # This is a placeholder - implement your own validation
    return True

# ============================================================================
# API Routes
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    }), 200

@app.route('/api/search', methods=['POST'])
@require_api_key
def search():
    """
    Main search endpoint
    
    POST /api/search
    {
        "query": "username or email",
        "type": "username|email|phone|hashtag|location",
        "platforms": ["twitter", "instagram"],
        "limit": 100,
        "filters": {...}
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Request body is required'
            }), 400
        
        query = data.get('query', '').strip()
        search_type = data.get('type', 'username')
        platforms = data.get('platforms', ['all'])
        limit = data.get('limit', 100)
        filters = data.get('filters', {})
        
        if not query:
            return jsonify({
                'status': 'error',
                'message': 'Query parameter is required'
            }), 400
        
        # Log search
        logger.info(f"Search initiated - Query: {query}, Type: {search_type}, Platforms: {platforms}")
        
        # Import search module
        from core.search_engine import SearchEngine
        
        # Initialize search engine
        search_engine = SearchEngine(config)
        
        # Perform search
        results = search_engine.search(
            query=query,
            search_type=search_type,
            platforms=platforms,
            limit=limit,
            filters=filters
        )
        
        return jsonify({
            'status': 'success',
            'results': results,
            'total': len(results),
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/user/<username>/<platform>', methods=['GET'])
@require_api_key
def get_user_profile(username, platform):
    """
    Get detailed user profile information
    
    GET /api/user/<username>/<platform>
    """
    try:
        from core.profiles import ProfileAnalyzer
        
        analyzer = ProfileAnalyzer(config)
        profile = analyzer.get_profile(username, platform)
        
        if not profile:
            return jsonify({
                'status': 'error',
                'message': f'User not found on {platform}'
            }), 404
        
        return jsonify({
            'status': 'success',
            'profile': profile,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Profile fetch error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/hashtag/analyze', methods=['POST'])
@require_api_key
def analyze_hashtag():
    """
    Analyze hashtag usage and trends
    
    POST /api/hashtag/analyze
    {
        "hashtag": "osint",
        "platforms": ["twitter", "instagram"],
        "limit": 100
    }
    """
    try:
        data = request.get_json()
        hashtag = data.get('hashtag', '').strip()
        platforms = data.get('platforms', ['all'])
        limit = data.get('limit', 100)
        
        if not hashtag:
            return jsonify({
                'status': 'error',
                'message': 'Hashtag parameter is required'
            }), 400
        
        from core.hashtag_analyzer import HashtagAnalyzer
        
        analyzer = HashtagAnalyzer(config)
        results = analyzer.analyze(hashtag, platforms, limit)
        
        return jsonify({
            'status': 'success',
            'hashtag': hashtag,
            'results': results,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Hashtag analysis error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/network/analyze', methods=['POST'])
@require_api_key
def analyze_network():
    """
    Analyze user network and connections
    
    POST /api/network/analyze
    {
        "username": "john_doe",
        "platform": "twitter",
        "depth": 2
    }
    """
    try:
        data = request.get_json()
        username = data.get('username')
        platform = data.get('platform')
        depth = data.get('depth', 1)
        
        from core.network_analyzer import NetworkAnalyzer
        
        analyzer = NetworkAnalyzer(config)
        graph_data = analyzer.analyze(username, platform, depth)
        
        return jsonify({
            'status': 'success',
            'graph': graph_data,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Network analysis error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/sentiment/analyze', methods=['POST'])
@require_api_key
def analyze_sentiment():
    """
    Analyze sentiment of posts/content
    
    POST /api/sentiment/analyze
    {
        "username": "john_doe",
        "platform": "twitter",
        "limit": 100
    }
    """
    try:
        data = request.get_json()
        username = data.get('username')
        platform = data.get('platform')
        limit = data.get('limit', 100)
        
        from core.sentiment_analyzer import SentimentAnalyzer
        
        analyzer = SentimentAnalyzer(config)
        sentiment_data = analyzer.analyze(username, platform, limit)
        
        return jsonify({
            'status': 'success',
            'sentiment': sentiment_data,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Sentiment analysis error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/email-lookup', methods=['POST'])
@require_api_key
def email_lookup():
    """
    Lookup social media accounts by email
    
    POST /api/email-lookup
    {
        "email": "user@example.com"
    }
    """
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        
        if not email:
            return jsonify({
                'status': 'error',
                'message': 'Email parameter is required'
            }), 400
        
        from core.lookup import EmailLookup
        
        lookup = EmailLookup(config)
        results = lookup.search(email)
        
        return jsonify({
            'status': 'success',
            'email': email,
            'results': results,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Email lookup error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/phone-lookup', methods=['POST'])
@require_api_key
def phone_lookup():
    """
    Lookup social media accounts by phone number
    
    POST /api/phone-lookup
    {
        "phone": "+1-555-0123"
    }
    """
    try:
        data = request.get_json()
        phone = data.get('phone', '').strip()
        
        if not phone:
            return jsonify({
                'status': 'error',
                'message': 'Phone parameter is required'
            }), 400
        
        from core.lookup import PhoneLookup
        
        lookup = PhoneLookup(config)
        results = lookup.search(phone)
        
        return jsonify({
            'status': 'success',
            'phone': phone,
            'results': results,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Phone lookup error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/report/generate', methods=['POST'])
@require_api_key
def generate_report():
    """
    Generate comprehensive investigation report
    
    POST /api/report/generate
    {
        "search_id": "abc123",
        "format": "pdf",
        "include_timeline": true,
        "include_network": true
    }
    """
    try:
        data = request.get_json()
        search_id = data.get('search_id')
        format_type = data.get('format', 'pdf')
        include_timeline = data.get('include_timeline', True)
        include_network = data.get('include_network', True)
        
        from core.report_generator import ReportGenerator
        
        generator = ReportGenerator(config)
        report_path = generator.generate(
            search_id=search_id,
            format_type=format_type,
            include_timeline=include_timeline,
            include_network=include_network
        )
        
        return jsonify({
            'status': 'success',
            'report_id': search_id,
            'download_url': f'/api/report/download/{search_id}',
            'format': format_type,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Report generation error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/report/download/<report_id>', methods=['GET'])
def download_report(report_id):
    """
    Download generated report
    
    GET /api/report/download/<report_id>
    """
    try:
        from core.report_generator import ReportGenerator
        
        generator = ReportGenerator(config)
        file_path = generator.get_report_path(report_id)
        
        if not os.path.exists(file_path):
            return jsonify({
                'status': 'error',
                'message': 'Report not found'
            }), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=f'osint_report_{report_id}.pdf'
        )
    
    except Exception as e:
        logger.error(f"Report download error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/export', methods=['POST'])
@require_api_key
def export_data():
    """
    Export search results
    
    POST /api/export
    {
        "search_id": "abc123",
        "format": "csv|json|xlsx"
    }
    """
    try:
        data = request.get_json()
        search_id = data.get('search_id')
        format_type = data.get('format', 'csv')
        
        from core.exporter import DataExporter
        
        exporter = DataExporter(config)
        file_path = exporter.export(search_id, format_type)
        
        if not os.path.exists(file_path):
            return jsonify({
                'status': 'error',
                'message': 'Data not found'
            }), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=f'osint_export_{search_id}.{format_type}'
        )
    
    except Exception as e:
        logger.error(f"Export error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# ============================================================================
# Web Interface Routes (SPA)
# ============================================================================

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_spa(path):
    """Serve SPA (Single Page Application)"""
    if path != "" and os.path.exists(f'web/build/{path}'):
        return send_file(f'web/build/{path}')
    return render_template('index.html')

# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'status': 'error',
        'message': 'Resource not found',
        'code': 404
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'status': 'error',
        'message': 'Internal server error',
        'code': 500
    }), 500

# ============================================================================
# Application Startup
# ============================================================================

if __name__ == '__main__':
    logger.info("Starting OSINT Social Media Tool Web Application")
    logger.info(f"Environment: {app.config.get('environment', 'development')}")
    logger.info(f"Debug mode: {app.config.get('debug', False)}")
    
    # Run Flask application
    app.run(
        host=config.get('server', {}).get('host', '127.0.0.1'),
        port=config.get('server', {}).get('port', 5000),
        debug=config.get('server', {}).get('debug', False),
        use_reloader=True
    )
