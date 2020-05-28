import csv
import urllib
from io import StringIO
from tqdm import tqdm

from data.models import AttachmentFile


csv_file_name = 'https://ucd52c9ac03f28a8ccad2f9a81f5.dl.dropboxusercontent.com/cd/0/get/A4gpsftyJP7KypBLsfgC_459cWJTfUqRusbbg8E4sU_ogyPM8f3Q8OzpQmrusrWfpSQygaR3q3s7STORTN8h9e_qJsRfVzgcNNtuaQgWxLvk-aFQUGamiurgP09IiJGIb9U/file#'
file_name_in_db = []
multiple_file_name = []
file_name_not_in_db = []

ftpstream = urllib.request.urlopen(csv_file_name)
text = ftpstream.read().decode('utf-8')
csvfile = csv.reader(StringIO(text), delimiter=',')  # with the appropriate encoding
csvfile = [row for row in csvfile]

for crid, file_name, _, batch_name, *__  in tqdm(csvfile):
    if '2019.12.02' in batch_name or '2020.01.31' in batch_name:
        attachment_count = AttachmentFile.objects.filter(allegation_id=crid, url__contains=file_name.replace('_', '-').replace(' ', '-')).count()
        if attachment_count == 0:
            file_name_not_in_db.append(file_name)
        elif attachment_count > 1:
            multiple_file_name.append(file_name)
        else:
            file_name_in_db.append(file_name)


print('In DB', len(file_name_in_db))
print('Not in DB', len(file_name_not_in_db))
print('Duplicate', len(multiple_file_name))
