from django.conf import settings
from re import match
from tqdm import tqdm

from documentcloud import DocumentCloud


client = DocumentCloud(settings.DOCUMENTCLOUD_USER, settings.DOCUMENTCLOUD_PASSWORD)
all_documents = client.documents.search('projectid:49649', data=True)

pattern = r'^CRID \d+$'
for document in tqdm(all_documents):
    if match(pattern, document.title):
        original_filename = document.data['filename'].replace('.pdf', '')
        document.title = f'{document.title} {original_filename}'
        document.save()


client = DocumentCloud(settings.DOCUMENTCLOUD_USER, settings.DOCUMENTCLOUD_PASSWORD)
all_documents = client.documents.search('account:23814-matt-chapman title:crid', data=True)

pattern = r'^CRID \d+$'
for document in tqdm(all_documents):
    if match(pattern, document.title) and not document.data and document.access == 'public':
        document.delete()
