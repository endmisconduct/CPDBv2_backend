import csv
from urllib.request import urlopen
from io import StringIO
from tqdm import tqdm
from django.conf import settings

from data.models import *
from documentcloud import DocumentCloud


ocr_file_url = 'https://uc56874951c47eec020f6a4ebbef.dl.dropboxusercontent.com/cd/0/get/A4qGUAGhfQGC8peHEf_zWocfCbuc905Hz4A-kUlAr7L4W6gZmLCNviCTY3IWhIGuiqBIFaCPwZDAbgCAH2v_f6S8t7qYKzqNFa_qWzvXOxbwvjj8YNkF9K6OEkZlLacj5ds/file#'
first_batch_csv_url = 'https://uc70e18978f8da5add6ad8256143.dl.dropboxusercontent.com/cd/0/get/A4lTpW0-ab1J5Cdjer1Y8p47s017O5ztAn_cGHLLSpp4VhYmo6e-pSv8s6u1mf__GLggJBZ1ty5pPo71YM684xYb351I08T_wpdy9ZIqs-DsNM37uNj0scbHUMkuJ8sS--I/file#'
third_batch_csv_url = 'https://ucaee6cb3a3871a6e05ce90ac938.dl.dropboxusercontent.com/cd/0/get/A4mxwuIwEZFIfFbvLvNVJSCxRaiKXbZermPnTMjOiwk7e-rHzm4bLkvvcm_UJdj7WCO8XSt2720BeXG1EewAQ4GA219HX8u0N6jPFJhQ9WOZtvlUmheKxFFgyHJq-DXNU8o/file#'

def read_remote_csv(url):
    ftp_stream = urlopen(url)
    text = ftp_stream.read().decode('utf-8')
    csv_file = csv.reader(StringIO(text), delimiter=',')
    return list(csv_file)

def create_mapping(csv_file):
    mapping = {}
    for file_name, file_title in csv_file[1:]:
        mapping[file_name] = file_title
    return mapping

ocr_csv_file = read_remote_csv(ocr_file_url)
data = set()
for crid, file_name, _, batch_name, _, _ in ocr_csv_file[1:]:
    data.add((crid, file_name, batch_name))

data = [list(row) for row in data]

first_batch_csv_file = read_remote_csv(first_batch_csv_url)
third_batch_csv_file = read_remote_csv(third_batch_csv_url)

first_batch_mapping = create_mapping(first_batch_csv_file)
third_batch_mapping = create_mapping(third_batch_csv_file)


client = DocumentCloud(settings.DOCUMENTCLOUD_USER, settings.DOCUMENTCLOUD_PASSWORD)

cloud_documents = []
missing_cloud_documents = []
missing_attachments = []


for crid, file_name, batch_name in tqdm(data):
    attachment = None
    if '2019_09_03' in batch_name:
        file_title = first_batch_mapping.get(file_name.replace('.pdf', ''))
        if file_title:
            attachment = AttachmentFile.objects.filter(allegation_id=crid, title__contains=file_title).first()
    elif '2019_12_02' in batch_name:
        attachment = AttachmentFile.objects.filter(allegation_id=crid, url__contains=file_name.replace('_', '-').replace(' ', '-')).first()
    elif '2019_12_30' in batch_name:
        file_title = third_batch_mapping.get(file_name.replace('.pdf', ''))
        if file_title:
            attachment = AttachmentFile.objects.filter(allegation_id=crid, title__contains=file_title).first()
    elif '2020_01_31' in batch_name:
        attachment = AttachmentFile.objects.filter(allegation_id=crid, url__contains=file_name.replace('_', '-').replace(' ', '-')).first()
    else:
        continue

    project = None
    if '2019_09_03' in batch_name:
        project = ''
    elif '2019_12_02' in batch_name:
        project = ''
    elif '2019_12_30' in batch_name:
        project = ''
    elif '2020_01_31' in batch_name:
        project = ''

    if attachment and attachment.external_id:
        cloud_document = client.documents.get(attachment.external_id)
        if cloud_document:
            cloud_document.data = { 'batch': batch_name, 'filename': file_name }
            cloud_document.project = project
            cloud_document.save()
            cloud_documents.append(attachment.external_id)
        else:
            missing_cloud_documents.append(attachment.external_id)
    else:
        missing_attachments.append((crid, file_name))


print('Updated cloud documents', len(set(cloud_documents)))
print('Missing cloud documents', len(set(missing_cloud_documents)))
print('Missing Attachments', len(set(missing_attachments)))

