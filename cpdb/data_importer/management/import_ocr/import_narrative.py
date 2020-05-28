import csv
from urllib.request import urlopen
from re import match
from io import StringIO
from tqdm import tqdm

from data.models import *


narrative_csv_url = 'https://ucab37b706bccf6e1823b5d1358d.dl.dropboxusercontent.com/cd/0/get/A4xvcNy_dMms30vCMVhiVBRYU_JOm0jjbZXaR2dxJmb7KDCsk2iMd9y4cBZAjW1isV2-O41deucZkLRJ-ROzxXJWxEW-gjZeHtilntOLMjFludvHpusJbnrLuztLgmiCFIo/file#'
first_batch_csv_url = 'https://uc87e93286ae11d3e65ecba69e9f.dl.dropboxusercontent.com/cd/0/get/A4xFGFOYIdC4EWWD-zVOKZgc_fvHS_lq39_X0lsU-AdYvj4H-CKPNh-Q5PSXLz-k_q9lHXGQ6ZwVy5msqwJZOI-zQ6QFK6Sa2lM_lQkzmtkMuWceTWwlrTXlyylU1V0ioU0/file#'
third_batch_csv_url = 'https://uc0fc2c8733de32218bcf8bdc9e1.dl.dropboxusercontent.com/cd/0/get/A4zxrJSrBYiHloMGb5wPHN49oSvzmudqtp_97J7_a7EqCmKFH_sXQ7AJaxPBaUtSY5ciPVaUb2dJoxDC4scvAkEU72jv8h7qsiMRT745m9BL0FwuLjGt-gfXZu__xhBJtms/file#'


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


narrative_csv_file = read_remote_csv(narrative_csv_url)[1:]
sorted_narrative_csv_file = list(sorted(narrative_csv_file, key=lambda row: row[1] + '_' + row[2]))
first_batch_csv_file = read_remote_csv(first_batch_csv_url)
third_batch_csv_file = read_remote_csv(third_batch_csv_url)

first_batch_mapping = create_mapping(first_batch_csv_file)
third_batch_mapping = create_mapping(third_batch_csv_file)

file_name_in_db = []
file_name_not_in_db = []
attachment_narratives = []

for crid, file_name, page_num, section_name, column_name, text_content, _, batch_name, doc_url in tqdm(sorted_narrative_csv_file):
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
        attachment = AttachmentFile.objects.filter(allegation_id=crid, url=doc_url).first()

    if attachment:
        file_name_in_db.append((crid, file_name, batch_name))
    else:
        file_name_not_in_db.append((crid, file_name, batch_name))

    if attachment:
        attachment_narratives.append(
            AttachmentNarrative(
                attachment=attachment,
                page_num=page_num,
                section_name=section_name,
                column_name=column_name,
                text_content=text_content
            )
        )

AttachmentNarrative.objects.bulk_create(attachment_narratives)

print('In DB', len(set(file_name_in_db)))
print('Not in DB', len(set(file_name_not_in_db)))

