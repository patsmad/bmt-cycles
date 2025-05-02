from src.util.util_io import readJSON, data_path
from requests import get

headers = readJSON('config')['headers']

def downloadFile(url, save_path):
    r = get(url, stream=True)
    with open(f'{data_path}/{save_path}', 'wb') as fd:
        for chunk in r.iter_content(chunk_size=128):
            fd.write(chunk)
