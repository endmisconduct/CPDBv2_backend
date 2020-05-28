import csv
import urllib.request
from io import StringIO
from tqdm import tqdm

from data.models import AttachmentFile


csv_file_name = 'https://ucf8398c61a6bea560746cc5b581.dl.dropboxusercontent.com/cd/0/get/A4j6YPVZM8NbrVNw8FiJGBNpRVRqzD-vp9HZpl0v9pnguj7pAQ3IWjGBPEIWNpCeUIMi2eBuZCCuSLk_Wkxf0ugWQzDKqVZh8ZvsseQv9Puy2Vb7tKT9YNMxIiplrLi3q6E/file#'

ftpstream = urllib.request.urlopen(csv_file_name)
text = ftpstream.read().decode('utf-8')
csvfile = csv.reader(StringIO(text), delimiter=',')  # with the appropriate encoding
data = [row for row in csvfile]

file_name_not_in_db = []
file_name_in_db = []
multiple_file_name = []

for _, new_fn in tqdm(data[1:]):
    attachment_count = AttachmentFile.objects.filter(title__contains=new_fn).count()
    if attachment_count == 0:
        file_name_not_in_db.append(new_fn)
    elif attachment_count > 1:
        multiple_file_name.append(new_fn)
    else:
        file_name_in_db.append(new_fn)

print('In DB', len(file_name_in_db))
print('Not in DB', len(file_name_not_in_db))
print('Duplicate', len(multiple_file_name))
