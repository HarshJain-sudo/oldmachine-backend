"""
WSGI config for oldmachine_backend project.
Modified for Vercel deployment.
"""

import os
import sys
from pathlib import Path
from io import BytesIO
from http.server import BaseHTTPRequestHandler

# Add project root to Python path (for Vercel)
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oldmachine_backend.settings')

# Get WSGI application
wsgi_application = get_wsgi_application()


class Handler(BaseHTTPRequestHandler):
    """
    Vercel-compatible HTTP request handler that wraps Django WSGI.
    """
    
    def do_GET(self):
        self._handle_request()
    
    def do_POST(self):
        self._handle_request()
    
    def do_PUT(self):
        self._handle_request()
    
    def do_PATCH(self):
        self._handle_request()
    
    def do_DELETE(self):
        self._handle_request()
    
    def do_OPTIONS(self):
        self._handle_request()
    
    def _handle_request(self):
        """Process request through Django WSGI."""
        # Read request body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else b''
        
        # Parse path and query string
        if '?' in self.path:
            path_info, query_string = self.path.split('?', 1)
        else:
            path_info = self.path
            query_string = ''
        
        # Build WSGI environ
        environ = {
            'REQUEST_METHOD': self.command,
            'SCRIPT_NAME': '',
            'PATH_INFO': path_info,
            'QUERY_STRING': query_string,
            'CONTENT_TYPE': self.headers.get('Content-Type', ''),
            'CONTENT_LENGTH': str(len(body)),
            'SERVER_NAME': 'localhost',
            'SERVER_PORT': '80',
            'SERVER_PROTOCOL': self.protocol_version,
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'https',
            'wsgi.input': BytesIO(body),
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': False,
            'wsgi.multiprocess': True,
            'wsgi.run_once': False,
        }
        
        # Add HTTP headers
        for key, value in self.headers.items():
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
        
        # Call WSGI application
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
            
            # Send response
            self.send_response(status_code[0])
            for header, value in response_headers:
                self.send_header(header, value)
            self.end_headers()
            
            # Send body
            body_bytes = b''.join(response_body)
            self.wfile.write(body_bytes)
            
        except Exception as e:
            # Error handling
            import traceback
            error_msg = f"Internal Server Error: {str(e)}\n{traceback.format_exc()}"
            self.send_response(500)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(error_msg.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Override to prevent default logging."""
        pass


# Export handler for Vercel (it expects a class)
handler = Handler

# Also export application for compatibility
application = wsgi_application
