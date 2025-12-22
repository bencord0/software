#!/usr/bin/env python
import os
import re
import requests
import shutil
import tarfile
from pathlib import Path
from tqdm import tqdm
from urllib.parse import urlparse

from semver import SemVer
from software_updater import save_and_symlink

REPO_SLUG = 'gravitational/teleport'
SOFTWARE_PREFIX = 'teleport'
SOFTWARE_PREFIX_SEPARATOR = f'{SOFTWARE_PREFIX}-'
SOFTWARE_SUFFIX = '-linux-amd64-bin'
SOFTWARE_SUFFIX_TAR = f'{SOFTWARE_SUFFIX}.tar.gz'
INDEX_URL = f'https://api.github.com/repos/{REPO_SLUG}/releases'
FETCH_URL = f'https://cdn.teleport.dev/{SOFTWARE_PREFIX_SEPARATOR}{{version}}{SOFTWARE_SUFFIX_TAR}'
SAVED_TARBALL = f'~/Software/{SOFTWARE_PREFIX_SEPARATOR}{{version}}{SOFTWARE_SUFFIX_TAR}'
UNPACKED_ROOT = f'~/Software/{SOFTWARE_PREFIX_SEPARATOR}{{version}}'
TAR_PREFIX = f'{SOFTWARE_PREFIX_SEPARATOR}{{version}}{SOFTWARE_SUFFIX_TAR}'
SYMLINK_PATH = f'~/Software/{SOFTWARE_PREFIX}'
PREFIX = 'teleport'


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

    print(f'latest version is: {latest_version[0]}')
    return latest_version[1]['tag_name']


def main():
    version = latest_version()
    save_and_symlink(FETCH_URL, SAVED_TARBALL, UNPACKED_ROOT, SYMLINK_PATH, version, PREFIX)


if __name__ == '__main__':
    main()
