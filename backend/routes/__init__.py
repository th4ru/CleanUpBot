"""
Routes initialization
"""
from flask import Blueprint

def register_routes(app):
    """Register all route blueprints"""
    from .system import system_bp
    from .cleanup import cleanup_bp
    
    app.register_blueprint(system_bp, url_prefix='/api')
    app.register_blueprint(cleanup_bp, url_prefix='/api')
