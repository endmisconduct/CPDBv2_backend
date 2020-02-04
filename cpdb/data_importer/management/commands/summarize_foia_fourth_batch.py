from collections import Counter
from csv import DictWriter
from os import listdir, path, rename

import logging
from re import match
from tqdm import tqdm

from django.core.management import BaseCommand

from data.models import Allegation

logger = logging.getLogger('data_importer.import_foia')


class Command(BaseCommand):
    def listdir_pdf_files(self, source_folder):
        return [filename for filename in listdir(source_folder) if filename.endswith('.pdf')]

    def standardize_file_name(self, raw_filename):
        pattern = r'^LOG_(\d+)'
        matched = match(pattern, raw_filename)
        return f'CRID {matched.group(1)} DOCUMENT {raw_filename}.pdf'

    def get_crid(self, filename):
        pattern = r'^LOG_(\d+)'
        matched = match(pattern, filename)
        return matched.group(1)

    def get_correct_filename(self, file_name):
        filename_without_extension = path.splitext(file_name)[0]
        return True, self.standardize_file_name(filename_without_extension)

    def get_existing_and_missing_crids(self, file_names):
        existing_crids = []
        missing_crids = []
        for file_name in file_names:
            crid = self.get_crid(file_name)
            if not Allegation.objects.filter(crid=crid).exists():
                missing_crids.append(crid)
            else:
                existing_crids.append(crid)
        return existing_crids, missing_crids

    def add_arguments(self, parser):
        parser.add_argument('source_folder', nargs='?', type=str, help='Documents source folder')

    def handle(self, *args, **options):
        source_folder = options['source_folder']
        raw_file_names = self.listdir_pdf_files(source_folder)

        crids, missing_crids = self.get_existing_and_missing_crids(raw_file_names)
        counter = dict(Counter(crids))
        import ipdb; ipdb.set_trace()
        results = []
        # for crid in counter:
        #     allegation = Allegation.objects.get(crid=crid)
        #     results.append({
        #         'crid': crid,
        #         'num_docs': counter[crid],
        #         'incident_date': allegation.incident_date and allegation.incident_date.strftime(format='%Y-%m-%d'),
        #         'start_date': allegation.first_start_date,
        #     })
        #
        # with open('report.csv', 'w', newline='') as csv_file:
        #     fieldnames = ['crid', 'num_docs', 'start_date', 'incident_date']
        #     writer = DictWriter(csv_file, fieldnames=fieldnames)
        #     writer.writeheader()
        #     for result in results:
        #         writer.writerow(result)
        #
        # print(f'{len(missing_crids)} CRs do not exist in our database: {missing_crids}')
