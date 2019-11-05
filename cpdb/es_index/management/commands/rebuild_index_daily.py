from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        call_command('rebuild_index', '--daily')
        call_command('rebuild_search_index', '--daily')
