from csv import DictReader
from os import listdir, path, rename

import logging
from re import match
from tqdm import tqdm

from django.core.management import BaseCommand

logger = logging.getLogger('data_importer.import_foia')

ROWS = {
    'control_number': 'Control Number',
    'production_begin': 'Production Begin',
    'production_end': 'Production End',
    'production_begin_attachment': 'Production Begin Attachment',
    'production_end_attachment': 'Production End Attachment',
    'file_name': 'File Name',
    'file_path': 'File Path',
}


class Command(BaseCommand):
    def standardize_file_name(self, filename):
        pattern = r'^LOG_(\d+)\.zip\?\d+-\d+\.LOG_\d+\.\d+\.(.+)'
        matched = match(pattern, filename)
        return f'CRID {matched.group(1)} {matched.group(2)}'.replace('_', ' ')

    def get_correct_filename(self, csv_contents, filename):
        for row in csv_contents:
            if row[ROWS['production_begin']] == filename:
                return True, self.standardize_file_name(row[ROWS['file_name']])
        return False, ''

    def add_arguments(self, parser):
        parser.add_argument('--source-folder', help='Documents source folder')
        parser.add_argument('--csv-file-name', help='Name of csv file')

    def handle(self, *args, **options):
        source_folder = options['source_folder']
        csv_file_name = options['csv_file_name']
        try:
            document_filenames = listdir(source_folder)
        except FileNotFoundError:
            print(f'Folder "{source_folder}" does not exist.')
            return

        document_filenames_without_pdf = [path.splitext(filename)[0] for filename in document_filenames]

        try:
            csv_file = open(csv_file_name, newline='')
        except FileNotFoundError:
            print(f'CSV file "{csv_file_name}" does not exist.')
            return

        csv_contents = list(DictReader(csv_file))
        csv_file.close()

        for filename in tqdm(document_filenames_without_pdf):
            found, correct_filename = self.get_correct_filename(csv_contents, filename)
            if found:
                rename(f'{source_folder}/{filename}.pdf', f'{source_folder}/{correct_filename}')
            else:
                print(f'File not renamed: {filename}.pdf')
