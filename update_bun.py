#!/usr/bin/env python
import os
import re
import requests
import shutil
import zipfile
from pathlib import Path
from tqdm import tqdm
from urllib.parse import urlparse

from semver import SemVer
from software_updater import save_zipball

INDEX_URL = 'https://api.github.com/repos/oven-sh/bun/releases'
FETCH_URL = 'https://github.com/oven-sh/bun/releases/download/bun-v{version}/bun-linux-x64.zip'
SAVED_ZIPBALL_PATH = '~/Software/bun-{version}-linux-x64.zip'
UNPACK_PATH = '~/Software/bun/bin'
UNPACK_TARGET = 'bun-{version}'
ARCHIVE_SOURCE = 'bun-linux-x64/bun'
SYMLINK_PATH = '~/Software/bun/bin/bun'


def latest_version():
    index = requests.get(INDEX_URL).json()

    latest_version: Tuple[SemVer, Dict] = None
    for entry in index:
        # Filter out prereleases
        if entry['draft'] or entry['prerelease']:
            continue

        # semver
        version = SemVer(entry['tag_name'].removeprefix('bun-'))
        if latest_version is None:
            latest_version = (version, entry)
        elif version > latest_version[0]:
            latest_version = (version, entry)
        else:
            continue

    if latest_version is None:
        raise RuntimeError("Couldn't find latest lts version")

    return latest_version[0].version


def main():
    version = latest_version()
    fetch_url = FETCH_URL.format(version=version)

    saved_zipball = Path(SAVED_ZIPBALL_PATH.format(version=version)).expanduser()
    if not saved_zipball.exists():
        save_zipball(fetch_url, saved_zipball)

    unpack_path = Path(UNPACK_PATH).expanduser()
    if not unpack_path.exists():
        unpack_path.mkdir(parents=True)

    target_path = unpack_path / UNPACK_TARGET.format(version=version)
    with zipfile.ZipFile(saved_zipball) as archive:
        with archive.open(ARCHIVE_SOURCE) as source, \
             open(target_path, 'wb') as target:
            shutil.copyfileobj(source, target)
    target_path.chmod(0o755)

    symlink = Path(SYMLINK_PATH).expanduser()
    if symlink.exists():
        symlink.unlink()
    symlink.symlink_to(target_path)

if __name__ == '__main__':
    main()
