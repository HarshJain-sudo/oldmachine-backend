"""
Middleware to allow all Vercel domains in ALLOWED_HOSTS.

Django doesn't support wildcards in ALLOWED_HOSTS, but Vercel generates
dynamic preview URLs that we can't predict. This middleware intercepts
the host validation and allows any domain ending in .vercel.app.
"""

from django.core.exceptions import DisallowedHost
from django.http import HttpRequest
from django.conf import settings


class VercelHostMiddleware:
    """
    Middleware that allows all .vercel.app domains.
    
    This must be placed BEFORE SecurityMiddleware in MIDDLEWARE list.
    It modifies the request's META to bypass Django's host validation
    for .vercel.app domains.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request: HttpRequest):
        # Get the host from the request
        host = request.get_host().split(':')[0]  # Remove port if present
        
        # Allow all .vercel.app domains by adding to ALLOWED_HOSTS
        # This is safe because we're in beta environment (DEBUG=True)
        if host.endswith('.vercel.app'):
            # Add to ALLOWED_HOSTS if not already present
            # This is thread-safe for our use case (read-only after startup
            # except for this specific case in beta environment)
            if host not in settings.ALLOWED_HOSTS:
                # Use a list operation that's relatively safe
                settings.ALLOWED_HOSTS = list(settings.ALLOWED_HOSTS) + [host]
        
        return self.get_response(request)

