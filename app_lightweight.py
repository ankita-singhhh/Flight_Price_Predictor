"""
Lightweight Flask application for Vercel deployment
Optimized to reduce bundle size by moving ML model to serverless function
"""

from flask import Flask, request, jsonify, render_template
from datetime import datetime
import logging
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load configuration
try:
    from config import config
    app.config.from_object(config[os.getenv('FLASK_ENV', 'default')])
except ImportError:
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret')
    app.config['DEBUG'] = os.getenv('DEBUG', 'False').lower() == 'true'

# Routes
@app.route('/')
def home():
    """Home page - UI only"""
    return render_template('home.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model': 'XGBoost (Serverless)',
        'features': 643,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/predict', methods=['POST'])
def predict_api():
    """API endpoint that forwards to serverless function"""
    try:
        # Get prediction data
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['Dep_Time', 'Arrival_Time', 'stops', 'airline', 'Source', 'Destination']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Forward to serverless function
        import requests
        
        # Call serverless API (adjust URL for your deployment)
        api_url = os.getenv('API_URL', 'http://localhost:3000/api/predict')
        
        try:
            response = requests.post(api_url, json=data, timeout=10)
            response.raise_for_status()
            
            return jsonify(response.json()), response.status_code
        except requests.exceptions.RequestException as e:
            logger.error(f"Serverless API error: {e}")
            return jsonify({'error': f'Prediction service unavailable: {str(e)}'}), 503
            
    except Exception as e:
        logger.error(f"Prediction API error: {e}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config.get('DEBUG', False))
