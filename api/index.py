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

# Import Django
import django
django.setup()

# Import WSGI application
from oldmachine_backend.wsgi import application

# Vercel expects this to be the handler
handler = application

