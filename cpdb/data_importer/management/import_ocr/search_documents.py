from django.conf import settings

from documentcloud import DocumentCloud
from document_cloud.models import DocumentCloudSearchQuery


client = DocumentCloud(settings.DOCUMENTCLOUD_USER, settings.DOCUMENTCLOUD_PASSWORD)
search_syntaxes = DocumentCloudSearchQuery.objects.all().values_list('types', 'query')
all_documents = []
for _, syntax in search_syntaxes:
    all_documents += client.documents.search(syntax)
