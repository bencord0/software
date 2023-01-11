#!/usr/bin/env python
import requests
import subprocess
from pathlib import Path
from tqdm import tqdm

from semver import SemVer

INDEX_URL = 'https://zoom.us/rest/download?os=linux'
FETCH_URL = 'https://zoom.us/client/{version}/zoom_amd64.deb'


def latest_version():
    index = requests.get(INDEX_URL).json()
    return index['result']['downloadVO']['zoom']['version']


def save_deb(url, path):
    with path.open('wb') as binary:
        print(f'Downloading: {url}')
        download = requests.get(url, stream=True)

        with tqdm() as progress:
            for chunk in download.iter_content(chunk_size=4096):
                progress.update(len(chunk))
                binary.write(chunk)


def main():
    version = latest_version()
    fetch_url = FETCH_URL.format(version=version)

    saved_deb = Path(f'~/Software/zoom_amd64-{version}.deb').expanduser()
    if not saved_deb.exists():
        save_deb(fetch_url, saved_deb)

    subprocess.run(["sudo", "dpkg", "-i", str(saved_deb)], shell=True, check=True, capture_output=True)


if __name__ == '__main__':
    main()
