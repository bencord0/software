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

INDEX_URL = 'https://api.github.com/repos/argoproj/argo-cd/releases'
FETCH_URL = 'https://github.com/argoproj/argo-cd/releases/download/{version}/argocd-linux-amd64'


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


def save_binary(url, path):
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

    saved_binary = Path(f'~/Software/argocd-{version}').expanduser()
    if not saved_binary.exists():
        save_binary(fetch_url, saved_binary)

    saved_binary.chmod(0o755)

    symlink = Path('~/Software/argocd').expanduser()
    if symlink.exists():
        symlink.unlink()
    symlink.symlink_to(saved_binary)


if __name__ == '__main__':
    main()
