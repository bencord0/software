#!/usr/bin/env python
import os
import re
import requests
import shutil
from pathlib import Path
from tqdm import tqdm
from urllib.parse import urlparse

from software_updater import save_and_symlink

INDEX_URL = 'https://raw.githubusercontent.com/actions/go-versions/main/versions-manifest.json'
FETCH_URL = 'https://go.dev/dl/go{version}.linux-amd64.tar.gz'
SAVED_TARBALL = '~/Software/go{version}.linux-amd64.tar.gz'
UNPACKED_ROOT = '~/Software/go-{version}'
SYMLINK_PATH = '~/Software/go'
PREFIX = 'go'


def latest_version():
    index = requests.get(INDEX_URL).json()
    latest_version = index[0]['version']

    return latest_version


def main():
    version = latest_version()

    save_and_symlink(FETCH_URL, SAVED_TARBALL, UNPACKED_ROOT, SYMLINK_PATH, version, PREFIX)

if __name__ == '__main__':
    main()
