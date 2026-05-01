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
        csv_path = Path(settings.BASE_DIR).parent / 'source_files' / 'parsed_data.csv'
        with open(str(csv_path), mode='r', encoding='latin-1') as line:
            reader = csv.reader(line)
            for row in reader:
                pushin.append((row[0], row[1], row[2], row[3], row[4], 'imported'))
        MESSAGE = (
            'CREATE TABLE IF NOT EXISTS grade_results('
            'acceptance_year INT NOT NULL, '
            'program VARCHAR(255) NOT NULL, '
            'university_name VARCHAR(255) NOT NULL, '
            'admission_average INT NOT NULL, '
            'acceptance_status VARCHAR(255) NOT NULL, '
            'userid VARCHAR(255) NOT NULL DEFAULT "anonymous", '
            'CONSTRAINT chk_grade_results_admission_average '
            'CHECK (admission_average >= 0 AND admission_average <= 100))'
        )
        with connection.cursor() as cursor:
            cursor.execute(MESSAGE)
            # clear existing rows to avoid duplicates
            cursor.execute('TRUNCATE TABLE grade_results')
            PUSH_MESSAGE = (
                'INSERT INTO grade_results('
                'acceptance_year, program, university_name, admission_average, acceptance_status, userid) '
                'VALUES (%s, %s, %s, %s, %s, %s)'
            )
            cursor.executemany(PUSH_MESSAGE, pushin)
            print(cursor.rowcount, 'records inserted')


