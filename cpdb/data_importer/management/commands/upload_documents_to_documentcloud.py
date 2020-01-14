from multiprocessing.pool import Pool
from os import listdir, path

from documentcloud import DocumentCloud

from django.core.management import BaseCommand
from django.conf import settings

from data.constants import AttachmentSourceType


def upload(document, source_folder):
    client = DocumentCloud(production_username, production_password)
    source_type = AttachmentSourceType.DOCUMENTCLOUD
    try:
        client.documents.upload(
            f'{source_folder}/{document}',
            title=path.splitext(document)[0],
            description=source_type,
            access='public',
            force_ocr=True
        )
    except Exception:
        print(f'{document} failed to upload to documentclould, good luck next time!')


class Command(BaseCommand):
    def listdir_pdf_files(self, source_folder):
        return [filename for filename in listdir(source_folder) if filename.endswith('.pdf')]

    def add_arguments(self, parser):
        parser.add_argument('--source-folder', help='Documents source folder')

    def handle(self, *args, **options):
        source_folder = options['source_folder']
        documents = self.listdir_pdf_files(source_folder)

        arguments = [(document, source_folder) for document in documents]

        with Pool(processes=10) as pool:
            pool.starmap(upload, arguments)
