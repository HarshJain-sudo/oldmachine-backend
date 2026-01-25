#!/bin/bash
# Script to collect static files for Vercel deployment

echo "Collecting static files..."
export DJANGO_ENV=beta
python manage.py collectstatic --noinput

echo "✅ Static files collected in staticfiles/ directory"
echo "📦 Make sure to commit the staticfiles/ directory to git"

