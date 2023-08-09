#!/usr/bin/env python
import os
import re
import requests
import shutil
import tarfile
from pathlib import Path
from tqdm import tqdm
from urllib.parse import urlparse

INDEX_URL = 'https://raw.githubusercontent.com/actions/go-versions/main/versions-manifest.json'
FETCH_URL = 'https://go.dev/dl/go{version}.linux-amd64.tar.gz'


def latest_version():
    index = requests.get(INDEX_URL).json()
    latest_version = index[0]['version']

    return latest_version


def save_tarball(url, path):
    with path.open('wb') as tarball:
        print(f'Downloading: {url}')
        download = requests.get(url, stream=True)
        content_length = int(download.headers['content-length'])

        with tqdm(total=content_length) as progress:
            for chunk in download.iter_content(chunk_size=4096):
                progress.update(len(chunk))
                tarball.write(chunk)


def save_member(archive, root, member, replace_prefix):
    path = Path(
        member.name.replace(replace_prefix, str(root), 1)
    )
    print(f'{str(path)}')

    if member.isdir():
        if not path.exists():
            path.mkdir(parents=True)

    elif member.isfile():
        content = archive.extractfile(member)

        # Set file content
        if not path.parent.exists():
            path.parent.mkdir(parents=True)
        buf = content.read()
        path.write_bytes(buf)

        # Set file attributes
        path.chmod(member.mode)

        # Set file timestamps
        os.utime(path, (member.mtime, member.mtime))

    elif member.issym():
        path.symlinik_to(member.linkname)

    else:
        print(f'{member.name}: Unknown member type')
        breakpoint()

def main():
    version = latest_version()
    fetch_url = FETCH_URL.format(version=version)
    saved_tarball = Path(f'~/Software/go{version}.linux-amd64.tar.gz').expanduser()
    if not saved_tarball.exists():
        save_tarball(fetch_url, saved_tarball)


    archive = tarfile.open(saved_tarball)
    unpacked_root = Path(f'~/Software/go-{version}').expanduser()
    tar_prefix = 'go'

    for member in archive:
        save_member(archive, unpacked_root, member, tar_prefix)

    symlink = Path('~/Software/go').expanduser()
    if symlink.exists():
        symlink.unlink()
    symlink.symlink_to(unpacked_root)

if __name__ == '__main__':
    main()
