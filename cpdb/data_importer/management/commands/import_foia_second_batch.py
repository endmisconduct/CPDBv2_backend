from csv import DictReader
from os import listdir, path, rename

import logging
from re import match
from tqdm import tqdm

from django.core.management import BaseCommand

from data.models import Allegation

logger = logging.getLogger('data_importer.import_foia')

ROWS = {
    'production_begin_bates': 'Production::Begin Bates',
    'production_end_bates': 'Production::End Bates',
    'log_number': 'Log Number',
}


class Command(BaseCommand):
    def listdir_pdf_files(self, source_folder):
        return [filename for filename in listdir(source_folder) if filename.endswith('.pdf')]

    def standardize_file_name(self, filename, raw_filename):
        pattern = r'^LOG_(\d+)'
        matched = match(pattern, filename)
        return f'CRID {matched.group(1)} DOCUMENT {raw_filename}.pdf'

    def get_crid(self, filename):
        pattern = r'^LOG_(\d+)'
        matched = match(pattern, filename)
        return matched.group(1)

    def get_correct_filename(self, csv_contents, filename):
        filename_without_extension = path.splitext(filename)[0]
        for row in csv_contents:
            if row[ROWS['production_begin_bates']] == filename_without_extension:
                return True, self.standardize_file_name(row[ROWS['log_number']], filename_without_extension)
        return False, ''

    def rename_raw_documents(self, source_folder, csv_contents):
        raw_documents = self.listdir_pdf_files(source_folder)
        file_count_before = len(raw_documents)
        not_renamed_files = []
        for filename in tqdm(raw_documents):
            found, correct_filename = self.get_correct_filename(csv_contents, filename)
            if found:
                # print(f'{source_folder}/{filename}', '--', f'{source_folder}/{correct_filename}')
                rename(f'{source_folder}/{filename}', f'{source_folder}/{correct_filename}')
            else:
                not_renamed_files.append(filename)
        file_count_after = len(self.listdir_pdf_files(source_folder))
        return not_renamed_files, file_count_before - file_count_after

    def count_missing_cr(self, csv_contents):
        none_existed_crid_count = 0
        for row in csv_contents:
            crid = self.get_crid(row[ROWS['log_number']])
            if not Allegation.objects.filter(crid=crid).exists():
                none_existed_crid_count += 1
        return none_existed_crid_count

    def add_arguments(self, parser):
        parser.add_argument('--source-folder', help='Documents source folder')
        parser.add_argument('--csv-file-name', help='Name of the csv file')

    # def dedup_log_number(self, contents):
    #     sorted_contents = sorted(contents, key=lambda content: content[ROWS['log_number']])
    #     import ipdb; ipdb.set_trace()
    #     for row in contents:
    #         pass
    #     return contents

    def handle(self, *args, **options):
        source_folder = options['source_folder']
        csv_file_name = options['csv_file_name']

        with open(csv_file_name, newline='') as csv_file:
            csv_contents = list(DictReader(csv_file))

        # csv_contents = self.dedup_log_number(csv_contents)

        none_existed_crid_count = self.count_missing_cr(csv_contents)
        not_renamed_files, missing_files_count = self.rename_raw_documents(source_folder, csv_contents)

        print(f'{none_existed_crid_count} CRs do not exist in our database.')
        print(f'{missing_files_count} files missing.')
        print(f'{len(not_renamed_files)} files were not renamed.')
        print(not_renamed_files)
