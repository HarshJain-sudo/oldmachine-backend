"""
Vercel serverless function entry point for Django.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oldmachine_backend.settings')

# Import and setup Django
import django
django.setup()

# Import WSGI application
from django.core.wsgi import get_wsgi_application

# Get WSGI application
application = get_wsgi_application()

# Vercel Python runtime handler
# Vercel will call this function with request object
def handler(request):
    """
    Vercel serverless function handler.
    """
    # Build WSGI environ from Vercel request
    environ = {
        'REQUEST_METHOD': request.method,
        'SCRIPT_NAME': '',
        'PATH_INFO': request.path,
        'QUERY_STRING': request.query_string.decode() if hasattr(request.query_string, 'decode') else str(request.query_string or ''),
        'CONTENT_TYPE': request.headers.get('content-type', ''),
        'CONTENT_LENGTH': str(len(request.body)) if request.body else '0',
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '80',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'wsgi.input': request.body if request.body else b'',
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': True,
        'wsgi.run_once': False,
    }
    
    # Add HTTP headers
    for key, value in request.headers.items():
        key = key.upper().replace('-', '_')
        if key not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
            key = f'HTTP_{key}'
        environ[key] = value
    
    # Response storage
    response_data = []
    status = [200]
    headers = []
    
    def start_response(status_line, response_headers):
        status[0] = int(status_line.split()[0])
        headers.extend(response_headers)
    
    # Call WSGI application
    result = application(environ, start_response)
    
    # Collect response body
    body = b''.join(result)
    if hasattr(result, 'close'):
        result.close()
    
    # Return response (Vercel Python format)
    return {
        'statusCode': status[0],
        'headers': dict(headers),
        'body': body.decode('utf-8') if isinstance(body, bytes) else body
    }
