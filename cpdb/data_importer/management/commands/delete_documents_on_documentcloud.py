from multiprocessing.pool import Pool
import logging

from django.core.management import BaseCommand

from document_cloud.search import search_all


def delete_cloud_document(document):
    document.delete()


class Command(BaseCommand):
    def handle(self, *args, **options):
        logger = logging.getLogger('crawler.update_documents')
        all_documents = search_all(logger)
        batch_provided_documents = [document for document in all_documents if document.description == 'BATCH_PROVIDED']

        with Pool(processes=10) as pool:
            pool.map(delete_cloud_document, batch_provided_documents)
