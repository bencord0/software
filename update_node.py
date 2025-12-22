#!/usr/bin/env python
import os
import re
import requests
import tarfile
from pathlib import Path
from tqdm import tqdm
from urllib.parse import urlparse

from software_updater import save_and_symlink

INDEX_URL = "https://nodejs.org/dist/index.json"
FETCH_URL = 'https://nodejs.org/dist/{version}/node-{version}-linux-x64.tar.xz'
SAVED_TARBALL = '~/Software/node-{version}-linux-x64.tar.xz'
UNPACKED_ROOT = '~/Software/node-{version}-linux-x64'
SYMLINK_PATH = '~/Software/node-linux-x64'


def latest_lts_version():
    index = requests.get(INDEX_URL).json()
    for entry in index:
        if entry['lts']:
            return entry['version']
    raise RuntimeError("Couldn't find latest lts version")


def main():
    version = latest_lts_version()
    prefix = f'node-{version}-linux-x64/'

    save_and_symlink(FETCH_URL, SAVED_TARBALL, UNPACKED_ROOT, SYMLINK_PATH, version, prefix)


if __name__ == '__main__':
    main()
