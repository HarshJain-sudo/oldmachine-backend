"""
Vercel serverless function entry point for Django.

Vercel's @vercel/python builder automatically wraps WSGI applications.
We just need to export the Django WSGI application as 'application'.
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

# Import and setup Django
try:
    import django
    django.setup()
    
    # Import WSGI application
    from django.core.wsgi import get_wsgi_application
    
    # Get WSGI application - Vercel's @vercel/python will wrap this
    application = get_wsgi_application()
    
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
    def application(environ, start_response):
        """Fallback WSGI app if Django fails to initialize."""
        status = '500 Internal Server Error'
        headers = [('Content-Type', 'text/plain; charset=utf-8')]
        start_response(status, headers)
        return [error_msg.encode('utf-8')]
