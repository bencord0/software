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
from software_updater import save_tarball, unpack_tarball

INDEX_URL = 'https://api.github.com/repos/kovidgoyal/calibre/releases'
FETCH_URL = 'https://github.com/kovidgoyal/calibre/releases/download/v{version}/calibre-{version}-x86_64.txz'


def latest_version():
    index = requests.get(INDEX_URL).json()

    latest_version: Tuple[SemVer, Dict] = None
    for entry in index:
        # Filter out prereleases
        if entry['draft'] or entry['prerelease']:
            continue

        # semver
        version = SemVer(entry['tag_name'])
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
    saved_tarball = Path(f'~/Software/calibre-{version}-x86_64.txz').expanduser()
    if not saved_tarball.exists():
        save_tarball(fetch_url, saved_tarball)

    unpack_path = Path(f'~/Software/calibre-{version}').expanduser()
    unpack_tarball(saved_tarball, unpack_path, None)

    symlink = Path('~/Software/calibre').expanduser()
    if symlink.exists():
        symlink.unlink()
    symlink.symlink_to(unpack_path)


if __name__ == '__main__':
    main()
