import os
import inspect

from django.test import TestCase
from django.core.management import call_command

from robber import expect


class ImportFoiaTestCase(TestCase):
    def setUp(self):
        self.test_dir = os.path.dirname(inspect.getfile(self.__class__))
        os.mkdir(f'{self.test_dir}/document_source_folder')

    def tearDown(self):
        os.rmdir(f'{self.test_dir}/document_source_folder')

    def test_handle_with_incorrect_source_folder(self):
        expect(lambda: call_command(
            'import_foia',
            source_folder='Incorrect source folder',
            csv_file_name='test_foia.csv'
        )).to.throw(FileNotFoundError)

    def test_handle_with_incorrect_csv_file_name(self):
        expect(lambda: call_command(
            'import_foia',
            source_folder='document_source_folder',
            csv_file_name='test_foia.csv'
        )).to.throw(FileNotFoundError)

