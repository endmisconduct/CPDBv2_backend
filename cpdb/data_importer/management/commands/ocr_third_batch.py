from csv import DictReader, writer

import logging
from re import match

from django.core.management import BaseCommand

logger = logging.getLogger('data_importer.import_foia')


class Command(BaseCommand):
    def standardize_file_title(self, filename):
        pattern = r'^LOG_(\d+)\.zip\?\d+-\d+\.LOG_\d+\.\d+\.(.+)(\.[A-Za-z]+)$'
        matched = match(pattern, filename)
        return f'CRID {matched.group(1)} {matched.group(2)}'.replace('_', ' ')

    def get_correct_filenames(self, csv_contents):
        return [
            [row['Production::Begin Bates'], self.standardize_file_title(row['File Name'])]
            for row in csv_contents
        ]

    def add_arguments(self, parser):
        parser.add_argument('--csv-file-name', help='Name of the csv file')
        parser.add_argument('--export-csv-file-name', help='Name of the export csv file')

    def handle(self, *args, **options):
        csv_file_name = options['csv_file_name']
        export_csv_file_name = options['export_csv_file_name']

        with open(csv_file_name, newline='') as csv_file:
            csv_contents = list(DictReader(csv_file))

        with open(export_csv_file_name, mode='w') as csv_file:
            employee_writer = writer(csv_file, delimiter=',', quotechar='"')

            fieldnames = ['File name', 'File title']
            employee_writer.writerow(fieldnames)

            for row_data in self.get_correct_filenames(csv_contents):
                employee_writer.writerow(row_data)
