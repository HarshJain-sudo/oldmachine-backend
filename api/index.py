"""
Vercel serverless function entry point for Django.

This file provides the handler function that Vercel's Python runtime
expects. It bridges Vercel's serverless function format to Django's WSGI.
"""

import os
import sys
from pathlib import Path
from io import BytesIO

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
            from django.core.wsgi import get_wsgi_application
            _wsgi_application = get_wsgi_application()
        except Exception as e:
            # Log error but don't fail silently
            import traceback
            error_msg = (
                f"Django initialization failed: {str(e)}\n"
                f"{traceback.format_exc()}"
            )
            print(error_msg, file=sys.stderr)
            raise
    return _wsgi_application


def handler(req, res):
    """
    Vercel serverless function handler.
    
    This is the correct format for Vercel's Python runtime:
    - Takes (req, res) parameters
    - req: Request object with .method, .path, .headers, .body
    - res: Response object with .status(), .set_header(), .send()
    
    Args:
        req: Vercel request object
        res: Vercel response object
    """
    try:
        # Get Django WSGI application (lazy-loaded)
        wsgi_app = get_wsgi_app()
        
        # Extract request data with safe defaults
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
        elif body is None:
            body = b''
        
        # Build WSGI environ dict (required by WSGI spec)
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
        
        # Add HTTP headers to environ (WSGI format: HTTP_*)
        for key, value in headers.items():
            if value is None:
                continue
            key_upper = key.upper().replace('-', '_')
            if key_upper not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
                environ[f'HTTP_{key_upper}'] = str(value)
        
        # Response storage (using lists for closure)
        status_code = [200]
        response_headers = []
        response_body = []
        
        def start_response(status, headers):
            """WSGI start_response callback."""
            status_code[0] = int(status.split()[0])
            response_headers.extend(headers)
        
        # Call Django WSGI application
        result = wsgi_app(environ, start_response)
        
        # Collect response body
        try:
            for chunk in result:
                if isinstance(chunk, bytes):
                    response_body.append(chunk)
                elif isinstance(chunk, str):
                    response_body.append(chunk.encode('utf-8'))
                else:
                    response_body.append(str(chunk).encode('utf-8'))
        finally:
            # Ensure result is closed if it has a close method
            if hasattr(result, 'close'):
                try:
                    result.close()
                except Exception:
                    pass  # Ignore close errors
        
        # Build response
        body_bytes = b''.join(response_body)
        try:
            body_str = body_bytes.decode('utf-8')
        except UnicodeDecodeError:
            # If decoding fails, return as-is (might be binary)
            body_str = body_bytes.decode('utf-8', errors='replace')
        
        # Send response using Vercel's response object
        res.status(status_code[0])
        for header, value in response_headers:
            res.set_header(header, value)
        res.send(body_str)
        
    except Exception as e:
        # Comprehensive error handling
        import traceback
        error_msg = (
            f"Internal Server Error: {str(e)}\n"
            f"Type: {type(e).__name__}\n"
            f"Traceback:\n{traceback.format_exc()}"
        )
        
        # Log to stderr (visible in Vercel logs)
        print(error_msg, file=sys.stderr)
        
        # Send error response
        try:
            res.status(500)
            res.set_header('Content-Type', 'text/plain; charset=utf-8')
            res.send(error_msg)
        except Exception:
            # If even error response fails, there's nothing we can do
            pass
