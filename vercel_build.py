"""Vercel build step: apply migrations, then seed demo data on a fresh database."""
import os

import django
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.settings')
django.setup()

call_command('migrate', interactive=False)
call_command('seed_demo')
