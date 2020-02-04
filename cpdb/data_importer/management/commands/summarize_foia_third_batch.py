from collections import Counter
from csv import DictReader, DictWriter
from os import listdir, path, rename

import logging
from re import match
from tqdm import tqdm

from django.core.management import BaseCommand

from data.models import Allegation

logger = logging.getLogger('data_importer.import_foia')

ROWS = {
    'control_number': 'Control Number',
    'production_begin': 'Production::Begin Bates',
    'production_end': 'Production::End Bates',
    'production_begin_attachment': 'Production Begin Attachment',
    'production_end_attachment': 'Production End Attachment',
    'file_name': 'File Name',
    'file_path': 'File Path',
}


class Command(BaseCommand):
    def listdir_pdf_files(self, source_folder):
        return [filename for filename in listdir(source_folder) if filename.endswith('.pdf')]

    def standardize_file_name(self, filename):
        pattern = r'^LOG_(\d+)\.zip\?\d+-\d+\.LOG_\d+\.\d+\.(.+)(\.[A-Za-z]+)$'
        matched = match(pattern, filename)
        return f'CRID {matched.group(1)} {matched.group(2)}.pdf'.replace('_', ' ')

    def get_crid(self, filename):
        pattern = r'^LOG_(\d+)\.zip\?\d+-\d+\.LOG_\d+\.\d+\.(.+)'
        matched = match(pattern, filename)
        return matched.group(1)

    def get_correct_filename(self, csv_contents, filename):
        filename_without_extension = path.splitext(filename)[0]
        for row in csv_contents:
            if row[ROWS['production_begin']] == filename_without_extension:
                return True, self.standardize_file_name(row[ROWS['file_name']])
        return False, ''

    def rename_raw_documents(self, source_folder, csv_contents):
        raw_documents = self.listdir_pdf_files(source_folder)
        file_count_before = len(raw_documents)
        not_renamed_files = []
        for filename in tqdm(raw_documents):
            found, correct_filename = self.get_correct_filename(csv_contents, filename)
            if found:
                rename(f'{source_folder}/{filename}', f'{source_folder}/{correct_filename}')
            else:
                not_renamed_files.append(filename)
        file_count_after = len(self.listdir_pdf_files(source_folder))
        return not_renamed_files, file_count_before - file_count_after

    def get_existing_and_missing_crids(self, csv_contents):
        existing_crids = []
        missing_crids = []
        for row in csv_contents:
            crid = self.get_crid(row['File Name'])

            if not Allegation.objects.filter(crid=crid).exists():
                missing_crids.append(crid)
            else:
                existing_crids.append(crid)
        return existing_crids, missing_crids

    def add_arguments(self, parser):
        parser.add_argument('--csv-file-name', help='Name of the csv file')

    def handle(self, *args, **options):
        csv_file_name = options['csv_file_name']

        with open(csv_file_name, newline='') as csv_file:
            csv_contents = list(DictReader(csv_file))

        crids, missing_crids = self.get_existing_and_missing_crids(csv_contents)
        counter = dict(Counter(crids))
        results = []
        for crid in counter:
            allegation = Allegation.objects.get(crid=crid)
            results.append({
                'crid': crid,
                'num_docs': counter[crid],
                'incident_date': allegation.incident_date and allegation.incident_date.strftime(format='%Y-%m-%d'),
                'start_date': allegation.first_start_date,
            })

        with open('report.csv', 'w', newline='') as csv_file:
            fieldnames = ['crid', 'num_docs', 'start_date', 'incident_date']
            writer = DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for result in results:
                writer.writerow(result)

        print(f'{len(missing_crids)} CRs do not exist in our database: {missing_crids}')
