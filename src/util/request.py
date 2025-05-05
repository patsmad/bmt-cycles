from bs4 import BeautifulSoup as BS
import requests
from src.util.util_io import readJSON, data_path

headers: str = readJSON('config')['headers']

def downloadFile(url: str, save_path: str) -> None:
    r = requests.get(url, stream=True)
    with open(f'{data_path}/{save_path}', 'wb') as fd:
        for chunk in r.iter_content(chunk_size=128):
            fd.write(chunk)

def requestURL(url: str, cache: bool=True, cookie: str=None) -> requests.Response:
    if not cache:
        headers['Cache-Control'] = 'no-cache'
    if cookie is not None:
        headers['cookie'] = cookie
    return requests.get(url, timeout=60.0, headers=headers)

def soupifyURL(url: str, cache: bool=True, cookie: str=None) -> BS:
    with requestURL(url, cache, cookie) as request:
        return BS(request.text, 'html.parser')
