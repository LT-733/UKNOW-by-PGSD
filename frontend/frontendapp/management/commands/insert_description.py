from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings
from pathlib import Path
import csv

class Command(BaseCommand):
    help = "Pushes rows of data from csv file into mySQL database"
    def handle(self, *args, **options):
        self.push()
    def push(self):
        pushin = []
        csv_path = Path(settings.BASE_DIR).parent / 'source_files' / 'new_program_descriptions.csv'
        with open(str(csv_path), mode='r', encoding='latin-1') as line:
            reader = csv.reader(line)
            for row in reader:
                pushin.append((row[0], row[1], row[2], row[3]))
        MESSAGE = (
            'CREATE TABLE IF NOT EXISTS program_descriptions('
            'university varchar(255), '
            'program TEXT, '
            'description TEXT, '
            'link TEXT'
            ')'
        )
        with connection.cursor() as cursor:
            cursor.execute(MESSAGE)
            # clear existing rows to avoid duplicates
            cursor.execute('TRUNCATE TABLE program_descriptions')
            PUSH_MESSAGE = (
                'INSERT INTO program_descriptions('
                'university, program, description, link) '
                'VALUES (%s, %s, %s, %s)'
            )
            cursor.executemany(PUSH_MESSAGE, pushin)
            print(cursor.rowcount, 'records inserted')