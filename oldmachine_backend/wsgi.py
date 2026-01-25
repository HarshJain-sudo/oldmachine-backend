"""
WSGI config for oldmachine_backend project.
Modified for Vercel deployment using proper serverless function format.
"""

import os
import sys
from pathlib import Path
from io import BytesIO

# Add project root to Python path (for Vercel)
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Set Django settings module BEFORE importing Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oldmachine_backend.settings')

# Import and setup Django
import django
django.setup()

from django.core.wsgi import get_wsgi_application

# Get WSGI application
wsgi_application = get_wsgi_application()


def handler(req, res):
    """
    Vercel serverless function handler.
    
    This is the correct format for Vercel's Python runtime:
    - Takes (req, res) parameters
    - req: Request object with .method, .path, .headers, .body
    - res: Response object with .status(), .set_header(), .send()
    """
    # Extract request data
    method = getattr(req, 'method', 'GET') or 'GET'
    path = getattr(req, 'path', '/') or '/'
    headers = getattr(req, 'headers', {}) or {}
    body = getattr(req, 'body', b'') or b''
    
    # Handle query string
    if '?' in path:
        path_info, query_string = path.split('?', 1)
    else:
        path_info = path
        query_string = ''
    
    # Convert body to bytes if needed
    if isinstance(body, str):
        body = body.encode('utf-8')
    
    # Build WSGI environ dict
    environ = {
        'REQUEST_METHOD': method,
        'SCRIPT_NAME': '',
        'PATH_INFO': path_info,
        'QUERY_STRING': query_string,
        'CONTENT_TYPE': headers.get('content-type', ''),
        'CONTENT_LENGTH': str(len(body)),
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '80',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'wsgi.input': BytesIO(body),
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': True,
        'wsgi.run_once': False,
    }
    
    # Add HTTP headers to environ
    for key, value in headers.items():
        key_upper = key.upper().replace('-', '_')
        if key_upper not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
            environ[f'HTTP_{key_upper}'] = value
    
    # Response storage
    status_code = [200]
    response_headers = []
    response_body = []
    
    def start_response(status, headers):
        """WSGI start_response callback."""
        status_code[0] = int(status.split()[0])
        response_headers.extend(headers)
    
    # Call Django WSGI application
    try:
        result = wsgi_application(environ, start_response)
        
        # Collect response body
        for chunk in result:
            if isinstance(chunk, bytes):
                response_body.append(chunk)
            else:
                response_body.append(chunk.encode('utf-8'))
        
        if hasattr(result, 'close'):
            result.close()
        
        # Build response
        body_bytes = b''.join(response_body)
        body_str = body_bytes.decode('utf-8')
        
        # Send response using Vercel's response object
        res.status(status_code[0])
        for header, value in response_headers:
            res.set_header(header, value)
        res.send(body_str)
        
    except Exception as e:
        # Error handling with detailed traceback
        import traceback
        error_msg = f"Internal Server Error: {str(e)}\n{traceback.format_exc()}"
        res.status(500)
        res.set_header('Content-Type', 'text/plain')
        res.send(error_msg)


# Export application for compatibility (Django expects this)
application = wsgi_application
