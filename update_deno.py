#!/usr/bin/env python
import os
import re
import requests
import shutil
import zipfile
from pathlib import Path
from tqdm import tqdm
from urllib.parse import urlparse

INDEX_URL = 'https://api.github.com/repos/denoland/deno/releases'
FETCH_URL = 'https://github.com/denoland/deno/releases/download/{version}/deno-x86_64-unknown-linux-gnu.zip'


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


def save_zipball(url, path):
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
    saved_zipball = Path(f'~/Software/deno-x86_64-unknown-linux-gnu-{version}.zip').expanduser()
    if not saved_zipball.exists():
        save_zipball(fetch_url, saved_zipball)

    unpack_path = Path(f'~/Software/deno/bin').expanduser()
    if not unpack_path.exists():
        unpack_path.mkdir(parents=True)

    target_path = unpack_path / f'deno-{version}'
    with zipfile.ZipFile(saved_zipball) as archive:
        with archive.open('deno') as source, \
             open(target_path, 'wb') as target:
            shutil.copyfileobj(source, target)
    target_path.chmod(0o755)


    symlink = Path('~/Software/deno/bin/deno').expanduser()
    if symlink.exists():
        symlink.unlink()
    symlink.symlink_to(target_path)


if __name__ == '__main__':
    main()
