import os
import sys
from pathlib import Path
from django.db import connection

# Add the parent directory (Django project root) to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frontend.settings')

import django
django.setup()

import csv
from django.conf import settings

ProgramCheckingSource = Path(settings.BASE_DIR).parent / 'source_files' / 'new_program_descriptions.csv'
with connection.cursor() as cursor:
    university_msg = 'select university from program_descriptions'
    program_msg = 'SELECT program FROM program_descriptions'
    cursor.execute(university_msg)
    universitylist = [_[0].lower() for _ in cursor.fetchall()]
    cursor.execute(program_msg)
    programlist = [_[0].lower() for _ in cursor.fetchall()]
    print(universitylist)