import os
from os import makedirs, path
from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile

def get_f1_data(force: bool = False):
    if not os.path.exists('data/ergast'):
        os.makedirs('data/ergast')

    zipurl = 'http://ergast.com/downloads/f1db_csv.zip'
    with urlopen(zipurl) as zipresp:
        with ZipFile(BytesIO(zipresp.read())) as zfile:
            zfile.extractall('data/ergast')


if __name__ == "__main__":
    get_f1_data()