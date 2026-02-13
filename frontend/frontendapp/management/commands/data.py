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
        csv_path = Path(settings.BASE_DIR).parent / 'source_files' / 'totalreparsed.csv'
        with open(str(csv_path), mode='r', encoding='latin-1') as line:
            reader = csv.reader(line)
            for row in reader:
                pushin.append((row[0], row[1], row[2], row[3], row[4]))
        MESSAGE = (
            'CREATE TABLE IF NOT EXISTS grade_results('
            'acceptance_year int, '
            'program varchar(255), '
            'university_name varchar(255), '
            'admission_average int, '
            'acceptance_status varchar(255))'
        )
        with connection.cursor() as cursor:
            cursor.execute(MESSAGE)
            # clear existing rows to avoid duplicates
            cursor.execute('TRUNCATE TABLE grade_results')
            PUSH_MESSAGE = (
                'INSERT INTO grade_results('
                'acceptance_year, program, university_name, admission_average, acceptance_status) '
                'VALUES (%s, %s, %s, %s, %s)'
            )
            cursor.executemany(PUSH_MESSAGE, pushin)
            print(cursor.rowcount, 'records inserted')


