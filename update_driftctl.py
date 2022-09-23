#!/usr/bin/env python
import os
import re
import requests
import shutil
import zipfile
from pathlib import Path
from tqdm import tqdm
from urllib.parse import urlparse

INDEX_URL = 'https://api.github.com/repos/snyk/driftctl/releases'
FETCH_URL = 'https://github.com/snyk/driftctl/releases/download/{version}/driftctl_linux_amd64'


class SemVer():
    def __init__(self, version):
        major, minor, patch = version.split('.', 3)

        self._hash = hash(version)
        self._major = int(major.removeprefix('v'))
        self._minor = int(minor)
        self._patch = int(patch)

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        return (
            self._major == other._major
            and self._minor == other._minor
            and self._patch == other._patch
        )

    def __gt__(self, other):
        if self.__eq__(other):
            return False

        return (
            self._major >= other._major
            and self._minor >= other._minor
            and self._patch >= other._patch
        )


def latest_version():
    index = requests.get(INDEX_URL).json()

    latest_version: Tuple[SemVer, Dict] = None
    for entry in index:
        # Filter out prereleases
        if entry['draft'] or entry['prerelease']:
            continue

        # semver
        version = SemVer(entry['name'])
        if latest_version is None:
            latest_version = (version, entry)
        elif version > latest_version[0]:
            latest_version = (version, entry)
        else:
            continue

    if latest_version is None:
        raise RuntimeError("Couldn't find latest lts version")

    return latest_version[1]['name']


def save_binary(url, path):
    with path.open('wb') as tarball:
        print(f'Downloading: {url}')
        download = requests.get(url, stream=True)
        content_length = int(download.headers['content-length'])

        with tqdm(total=content_length) as progress:
            for chunk in download.iter_content(chunk_size=4096):
                progress.update(len(chunk))
                tarball.write(chunk)


def main():
    version = latest_version()
    fetch_url = FETCH_URL.format(version=version)

    saved_binary = Path(f'~/Software/driftctl-{version}').expanduser()
    if not saved_binary.exists():
        save_binary(fetch_url, saved_binary)

    saved_binary.chmod(0o755)

    breakpoint()
    symlink = Path('~/Software/driftctl').expanduser()
    if symlink.exists():
        symlink.unlink()
    symlink.symlink_to(saved_binary)


if __name__ == '__main__':
    main()
