"""
Flask App Initialization
WoosAI Backend API Server
"""

from flask import Flask
from flask_cors import CORS
import os


def create_app():
    """Create and configure Flask app"""
    
    app = Flask(__name__)
    
    # CORS configuration - Allow requests from your website
    CORS(app, 
         origins=[
             "http://localhost:8000",
             "http://127.0.0.1:8000", 
             "http://woos-ai.com",
             "https://woos-ai.com"
         ],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization"],
         supports_credentials=True
    )
    
    # App configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'woosai-secret-key-2025')
    app.config['MONGODB_URL'] = os.getenv('MONGODB_URL')
    app.config['DATABASE_NAME'] = os.getenv('DATABASE_NAME', 'woosai')
    app.config['STRIPE_SECRET_KEY'] = os.getenv('STRIPE_SECRET_KEY')
    app.config['STRIPE_PUBLISHABLE_KEY'] = os.getenv('STRIPE_PUBLISHABLE_KEY')
    
    # Register blueprints (routers)
    from app.routers.auth_router import auth_bp
    from app.routers.license_router import license_bp
    from app.routers.payment_router import payment_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(license_bp, url_prefix='/api/licenses')
    app.register_blueprint(payment_bp, url_prefix='/api/payments')
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return {'status': 'ok', 'message': 'WoosAI API is running'}
    
    
    
    return app