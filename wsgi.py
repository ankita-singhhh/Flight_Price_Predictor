"""WSGI entry point for production deployment."""

import os
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Try to import the main app, fallback to lightweight version
try:
    from app import app
except ImportError:
    from app_lightweight import app

from config import config

if __name__ == "__main__":
    config_name = os.getenv('FLASK_ENV', 'default')
    app.config.from_object(config[config_name])
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )
