import gzip
import json
import os
import shutil

file_path: str = os.path.dirname(os.path.realpath(__file__))
data_path: str = f'{file_path}/../..'

def make_dirs(fname: str) -> None:
    os.makedirs(f'{data_path}/{fname}', exist_ok=True)

def readJSON(fname: str) -> dict | list:
    with open(f'{data_path}/{fname}', 'r') as f:
        data = json.load(f)
    return data

def readTSV(fname):
    with open(f'{data_path}/{fname}', 'r', encoding="utf8") as f:
        rows = f.read().split('\n')
        headers = rows[0].split('\t')
        out = [{header: datum for header, datum in zip(headers, row.split('\t'))} for row in rows[1:-1]]
    return out

def removeFile(fname):
    os.remove(f'{data_path}/{fname}')

def streamTSV(fname, apply_method):
    out = []
    with open(f'{data_path}/{fname}', 'r', encoding="utf8") as f:
        headers = f.readline()
        line = f.readline()
        while line:
            transformed_row = apply_method(line, headers)
            if transformed_row:
                out.append(transformed_row)
            line = f.readline()
    return out

def unzipGZFile(fname):
    with gzip.open(f'{data_path}/{fname}', 'rb') as f_in:
        with open(f'{data_path}/{fname.replace('.gz', '')}', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    removeFile(fname)

