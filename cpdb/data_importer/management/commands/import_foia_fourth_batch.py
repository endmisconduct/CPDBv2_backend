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

    def rename_raw_documents(self, source_folder):
        raw_file_names = self.listdir_pdf_files(source_folder)
        file_count_before = len(raw_file_names)
        not_renamed_files = []
        for filename in tqdm(raw_file_names):
            found, correct_filename = self.get_correct_filename(filename)
            if found:
                rename(f'{source_folder}/{filename}', f'{source_folder}/{correct_filename}')
            else:
                not_renamed_files.append(filename)
        file_count_after = len(self.listdir_pdf_files(source_folder))
        return not_renamed_files, file_count_before - file_count_after

    def count_missing_cr(self, file_names):
        none_existed_crid_count = 0
        for file_name in file_names:
            crid = self.get_crid(file_name)
            if not Allegation.objects.filter(crid=crid).exists():
                none_existed_crid_count += 1
        return none_existed_crid_count

    def add_arguments(self, parser):
        parser.add_argument('--source-folder', help='Documents source folder')

    def handle(self, *args, **options):
        source_folder = options['source_folder']
        raw_file_names = self.listdir_pdf_files(source_folder)

        none_existed_crid_count = self.count_missing_cr(raw_file_names)
        not_renamed_files, missing_files_count = self.rename_raw_documents(source_folder)

        print(f'{none_existed_crid_count} CRs do not exist in our database.')
        print(f'{missing_files_count} files missing.')
        print(f'{len(not_renamed_files)} files were not renamed.')
        print(not_renamed_files)
