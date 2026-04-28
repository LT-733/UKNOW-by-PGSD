import os
import sys
from pathlib import Path

# Add the parent directory (Django project root) to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frontend.settings')

import django
django.setup()

import csv
from django.conf import settings

ProgramCheckingSource = Path(settings.BASE_DIR).parent / 'source_files' / 'new_program_descriptions.csv'
with open(str(ProgramCheckingSource), mode='r', encoding='latin-1') as line:
    reader = csv.reader(line)
    all_rows = list(reader)
    unichecklist = [_[0] for _ in all_rows]
    programchecklist = [_[1] for _ in all_rows]
    print(programchecklist)