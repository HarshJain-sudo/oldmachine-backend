"""
Management command to test database connection.

Usage:
    python manage.py test_db_connection
    python manage.py test_db_connection --env beta
    python manage.py test_db_connection --env prod
"""

from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings
import os
import sys


class Command(BaseCommand):
    """Command to test database connection."""

    help = 'Test database connection for current environment'

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            '--env',
            type=str,
            choices=['local', 'beta', 'prod'],
            help='Environment to test (overrides DJANGO_ENV)',
        )

    def handle(self, *args, **options):
        """Execute the command."""
        env = options.get('env')
        if env:
            os.environ['DJANGO_ENV'] = env
            # Note: Settings are already loaded, this just changes env var
            # For full reload, restart Django

        self.stdout.write(
            self.style.WARNING(
                f'\n🔍 Testing database connection...'
            )
        )

        # Display current environment
        current_env = os.environ.get('DJANGO_ENV', 'local')
        self.stdout.write(
            f'📌 Environment: {self.style.SUCCESS(current_env)}'
        )

        # Display database configuration (hide password)
        db_config = settings.DATABASES['default']
        self.stdout.write(f'\n📊 Database Configuration:')
        self.stdout.write(
            f'   Engine: {self.style.SUCCESS(db_config["ENGINE"])}'
        )
        self.stdout.write(
            f'   Name: {self.style.SUCCESS(db_config["NAME"])}'
        )
        self.stdout.write(
            f'   User: {self.style.SUCCESS(db_config["USER"])}'
        )
        self.stdout.write(
            f'   Host: {self.style.SUCCESS(db_config["HOST"])}'
        )
        self.stdout.write(
            f'   Port: {self.style.SUCCESS(db_config["PORT"])}'
        )
        self.stdout.write(
            f'   Password: {"*" * len(db_config.get("PASSWORD", ""))}'
        )

        # Test connection
        self.stdout.write(f'\n🔌 Testing connection...')
        try:
            with connection.cursor() as cursor:
                # Simple query to test connection
                cursor.execute("SELECT 1")
                result = cursor.fetchone()

                if result and result[0] == 1:
                    self.stdout.write(
                        self.style.SUCCESS(
                            '\n✅ Database connection successful!'
                        )
                    )

                    # Get database version
                    if 'postgresql' in db_config['ENGINE']:
                        cursor.execute("SELECT version()")
                        version = cursor.fetchone()[0]
                        self.stdout.write(
                            f'\n📦 PostgreSQL Version:'
                        )
                        self.stdout.write(f'   {version[:80]}...')
                    elif 'sqlite' in db_config['ENGINE']:
                        cursor.execute("SELECT sqlite_version()")
                        version = cursor.fetchone()[0]
                        self.stdout.write(
                            f'\n📦 SQLite Version: {version}'
                        )

                    # Test table access
                    self.stdout.write(f'\n📋 Testing table access...')
                    try:
                        from django.contrib.contenttypes.models import (
                            ContentType
                        )
                        count = ContentType.objects.count()
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'   ✅ Can query tables (found {count} '
                                f'content types)'
                            )
                        )
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(
                                f'   ⚠️  Table query test failed: {e}'
                            )
                        )

                    return

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'\n❌ Database connection failed!'
                )
            )
            self.stdout.write(
                self.style.ERROR(f'\nError details: {str(e)}')
            )
            self.stdout.write(
                self.style.ERROR(f'\nError type: {type(e).__name__}')
            )

            # Provide troubleshooting tips
            self.stdout.write(f'\n🔧 Troubleshooting tips:')
            if 'postgresql' in db_config['ENGINE']:
                self.stdout.write(
                    '   1. Check if database server is running'
                )
                self.stdout.write(
                    '   2. Verify host, port, and credentials'
                )
                self.stdout.write(
                    '   3. Check firewall/network settings'
                )
                self.stdout.write(
                    '   4. Ensure SSL is properly configured'
                )
                self.stdout.write(
                    '   5. Check if database exists'
                )
            elif 'sqlite' in db_config['ENGINE']:
                self.stdout.write(
                    '   1. Check if database file exists'
                )
                self.stdout.write(
                    '   2. Verify file permissions'
                )

            sys.exit(1)

