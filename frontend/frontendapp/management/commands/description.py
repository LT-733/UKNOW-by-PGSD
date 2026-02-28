from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings
from pathlib import Path
from playwright.sync_api import sync_playwright
import csv

class Command(BaseCommand):
    help = "Scrapes program description from the link https://universitystudy.ca/programs/"
    def handle(self, *args, **options):
        self.writer()
    def crawler(self, url: str):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            print(f"navigating to {url}")
            page.goto(url)

            try:
                page.wait_for_selector(".content.paragraph--regular", state= 'visible', timeout= 10000)
                print("Containter: content.paragraph--regular is visible.")

                page.wait_for_selector(".content.paragraph--regular p", state= 'attached', timeout= 5000)
                print("Child <p> elements are attached.")

            except Exception as e:
                print(f"error while waiting for elements:", e)
                print("The element may have taken too long to load, or they do not exist.")
                browser.close()
                return []
            
            container = page.locator('.content.paragraph--regular')
            p_elements = container.locator('p').all()
            #this is a list object
            extracted_texts = []
            for p_element in p_elements:
                text = p_element.text_content().strip()
                if text:
                    extracted_texts.append(text)

            browser.close()
            return extracted_texts
    def writer(self):
        fileName = 'program_description.csv'
        with open(fileName, 'w', newline='') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(['description'])

            url = 'https://universitystudy.ca/program/'
            for i in range (100000):
                texts = self.crawler(url + str(i))
                if texts:
                    for j, text in enumerate(texts):
                        #if j >= 1:
                        csv_writer.writerow([text])

