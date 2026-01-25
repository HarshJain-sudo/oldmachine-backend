"""
Vercel serverless function entry point for Django.

Vercel's Python runtime requires either:
- A 'handler' class (inheriting from BaseHTTPRequestHandler), OR
- An 'app' variable (WSGI application)

For Django, we export the WSGI application as 'app' which Vercel
automatically wraps for serverless execution.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Set Django settings module BEFORE importing Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oldmachine_backend.settings')

# Lazy-load Django to avoid initialization errors in serverless
_wsgi_application = None


def get_wsgi_app():
    """
    Lazy-load Django WSGI application.
    This prevents initialization errors during cold starts.
    """
    global _wsgi_application
    if _wsgi_application is None:
        try:
            import django
            django.setup()
            
            # Import WSGI application
            from django.core.wsgi import get_wsgi_application
            
            # Get WSGI application
            _wsgi_application = get_wsgi_application()
            
        except Exception as e:
            # Log error for debugging
            import traceback
            error_msg = (
                f"Django initialization failed: {str(e)}\n"
                f"Type: {type(e).__name__}\n"
                f"Traceback:\n{traceback.format_exc()}"
            )
            print(error_msg, file=sys.stderr)
            
            # Create a minimal WSGI app that returns an error
            def error_app(environ, start_response):
                """Fallback WSGI app if Django fails to initialize."""
                status = '500 Internal Server Error'
                headers = [
                    ('Content-Type', 'text/plain; charset=utf-8')
                ]
                start_response(status, headers)
                return [error_msg.encode('utf-8')]
            
            _wsgi_application = error_app
    
    return _wsgi_application


# Export as 'app' - Vercel's Python runtime expects this name
# for WSGI applications
app = get_wsgi_app()

# Also export as 'application' for compatibility
application = app
