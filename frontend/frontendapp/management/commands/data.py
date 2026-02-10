from django.core.management.base import BaseCommand
from django.db import connection
import csv

class Command(BaseCommand):
    help = "Pushes rows of data from csv file into mySQL database"
    def handle(self, *args, **options):
        self.push()
    def push(self):
        pushin = []
        with open('/Users/leon/Developer/UKNOW/source_files/totalreparsed.csv', mode='r', encoding='latin-1') as line:
            reader = csv.reader(line)
            for row in reader:
                pushin.append((row[0], row[1], row[2], row[3], row[4]))
        print(pushin)
        MESSAGE = 'CREATE TABLE IF NOT EXISTS grade_results(acceptance_year int, program varchar(255), university_name varchar(255), admission_average int, acceptance_status varchar(255))'
        with connection.cursor() as cursor:
            cursor.execute(MESSAGE)
            for row in pushin:
                PUSH_MESSAGE = "INSERT INTO grade_results(acceptance_year, program, university_name, admission_average, acceptance_status) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(PUSH_MESSAGE, row)
            print(cursor.rowcount, "record inserted") 


