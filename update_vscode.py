#!/usr/bin/env python
import os
import re
import requests
import tarfile
from pathlib import Path
from tqdm import tqdm
from urllib.parse import urlparse

from software_updater import save_and_symlink

URL = 'https://code.visualstudio.com/sha/download?build=stable&os=linux-x64'
SAVED_TARBALL = '~/Software/code-{version}.tar.gz'
UNPACKED_ROOT = '~/Software/VSCode-linux-x64-{version}'
SYMLINK_PATH = '~/Software/VSCode-linux-x64'
PREFIX = 'VSCode-linux-x64'

class LocationParser:
    def __init__(self, url: str):
        self.url = url
        self.parsed_url = urlparse(url)
        self.path = Path(self.parsed_url.path)

        # 'code-stable-x64-xxxxxxxx.tar.gz
        self.name = self.path.name
        self.version = re.fullmatch(
            r'code-stable-x64-(?P<version>\d+).tar.gz',
            self.name,
        )['version']


def main():
    redirect = requests.get(URL, allow_redirects=False)
    location = LocationParser(redirect.headers['location'])

    save_and_symlink(
        location.url,
        SAVED_TARBALL,
        UNPACKED_ROOT,
        SYMLINK_PATH,
        location.version,
        PREFIX,
    )


if __name__ == '__main__':
    main()
