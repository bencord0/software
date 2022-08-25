#!/usr/bin/env python
import os
import re
import requests
import shutil
import tarfile
from pathlib import Path
from tqdm import tqdm
from urllib.parse import urlparse

INDEX_URL = 'https://api.github.com/repos/helm/helm/releases'
FETCH_URL = 'https://get.helm.sh/helm-{version}-linux-amd64.tar.gz'


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
        version = SemVer(entry['tag_name'])
        if latest_version is None:
            latest_version = (version, entry)
        elif version > latest_version[0]:
            latest_version = (version, entry)
        else:
            continue

    if latest_version is None:
        raise RuntimeError("Couldn't find latest lts version")

    return latest_version[1]['tag_name']


def save_tarball(url, path):
    with path.open('wb') as tarball:
        print(f'Downloading: {url}')
        download = requests.get(url, stream=True)

        with tqdm() as progress:
            for chunk in download.iter_content(chunk_size=4096):
                progress.update(len(chunk))
                tarball.write(chunk)


def main():
    version = latest_version()
    fetch_url = FETCH_URL.format(version=version)

    saved_tarball = Path(f'~/Software/helm-{version}.tar').expanduser()
    if not saved_tarball.exists():
        save_tarball(fetch_url, saved_tarball)

    unpack_path = Path(f'~/Software/helm-{version}').expanduser()
    if not unpack_path.exists():
        unpack_path.mkdir(parents=True)
        (unpack_path / 'bin').mkdir()

    target_path = unpack_path / 'bin' / 'helm'
    archive = tarfile.open(saved_tarball)
    helm_bin_meta = archive.extractfile('linux-amd64/helm')
    helm_bin_content = helm_bin_meta.read()
    target_path.write_bytes(helm_bin_content)
    target_path.chmod(0o755)

    symlink = Path('~/Software/helm').expanduser()
    if symlink.exists():
        symlink.unlink()
    symlink.symlink_to(unpack_path)


if __name__ == '__main__':
    main()
