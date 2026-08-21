"""
Theophysics Backend API Server
Main Flask application integrating all API endpoints
"""

from flask import Flask, jsonify
from flask_cors import CORS
from api.definition_api import definition_bp
from api.fruits_of_spirit_api import fruits_bp
import os

app = Flask(__name__)
CORS(app)

app.register_blueprint(definition_bp)
app.register_blueprint(fruits_bp)


@app.route('/')
def index():
    """Root endpoint with API information"""
    return jsonify({
        'name': 'Theophysics Backend API',
        'version': '1.0.0',
        'description': 'Definition Processor and Fruits of Spirit API',
        'endpoints': {
            'definitions': '/api/definitions/',
            'fruits_of_spirit': '/api/fruits-of-spirit/',
            'health': '/health',
            'docs': '/docs'
        }
    })


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'theophysics-backend',
        'version': '1.0.0'
    })


@app.route('/docs')
def docs():
    """API documentation endpoint"""
    return jsonify({
        'documentation': 'See README_GITHUB.md for full documentation',
        'definition_endpoints': {
            'POST /api/definitions/chat': 'Chat with AI processor',
            'POST /api/definitions/extract': 'Extract definitions from file',
            'POST /api/definitions/create': 'Create new definition',
            'POST /api/definitions/batch': 'Batch process files',
            'POST /api/definitions/guided': 'Guided extraction',
            'GET /api/definitions/template': 'Get YAML template',
            'GET /api/definitions/status': 'Check processor status'
        },
        'fruits_endpoints': {
            'GET /api/fruits-of-spirit/': 'Get all fruits',
            'GET /api/fruits-of-spirit/<id>': 'Get fruit by ID',
            'GET /api/fruits-of-spirit/name/<name>': 'Get fruit by name',
            'GET /api/fruits-of-spirit/greek/<word>': 'Get fruit by Greek word',
            'GET /api/fruits-of-spirit/physics-mapping': 'Get physics mappings',
            'GET /api/fruits-of-spirit/consciousness-mapping': 'Get consciousness mappings',
            'GET /api/fruits-of-spirit/search': 'Search fruits',
            'POST /api/fruits-of-spirit/compare': 'Compare fruits',
            'GET /api/fruits-of-spirit/random': 'Get random fruit',
            'GET /api/fruits-of-spirit/theophysics-integration': 'Get integration view'
        }
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Not found',
        'message': 'The requested endpoint does not exist',
        'available_endpoints': ['/api/definitions/', '/api/fruits-of-spirit/', '/health', '/docs']
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'production') == 'development'
    
    print("=" * 70)
    print("THEOPHYSICS BACKEND API SERVER")
    print("=" * 70)
    print(f"\nServer starting on http://localhost:{port}")
    print("\nAvailable endpoints:")
    print(f"  - http://localhost:{port}/")
    print(f"  - http://localhost:{port}/api/definitions/")
    print(f"  - http://localhost:{port}/api/fruits-of-spirit/")
    print(f"  - http://localhost:{port}/health")
    print(f"  - http://localhost:{port}/docs")
    print("\nPress CTRL+C to stop\n")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
