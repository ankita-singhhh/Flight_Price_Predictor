"""WSGI entry point for production deployment."""

import os
from app import app
from config import config

# Get configuration
env = os.getenv('FLASK_ENV', 'production')
app.config.from_object(config[env])

if __name__ == "__main__":
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )
