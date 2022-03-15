#!/usr/bin/env python
import os
import re
import requests
import tarfile
from pathlib import Path
from tqdm import tqdm
from urllib.parse import urlparse

INDEX_URL = "https://nodejs.org/dist/index.json"
FETCH_URL = 'https://nodejs.org/dist/{version}/node-{version}-linux-x64.tar.xz'


def latest_lts_version():
    index = requests.get(INDEX_URL).json()
    for entry in index:
        if entry['lts']:
            return entry['version']
    raise RuntimeError("Couldn't find latest lts version")


def save_tarball(url, path):
    with path.open('wb') as tarball:
        print(f'Downloading: {url}')
        download = requests.get(url, stream=True)
        content_length = int(download.headers['content-length'])

        with tqdm(total=content_length) as progress:
            for chunk in download.iter_content(chunk_size=4096):
                progress.update(len(chunk))
                tarball.write(chunk)


def save_member(archive, root, member, root_tar_dir):
    path = Path(
        member.name.replace(root_tar_dir, str(root), 1)
    )
    print(f'{str(path)}')

    if member.isdir():
        if not path.exists():
            path.mkdir()

    elif member.isfile():
        content  = archive.extractfile(member)

        # Set file content
        buf = content.read()
        path.write_bytes(buf)

        # Set file attribute bits
        path.chmod(member.mode)

        # Set file timestamps
        # Path.utime(member.mtime) does not yet exists
        os.utime(path, (member.mtime, member.mtime))
    elif member.issym():
        path.symlink_to(member.linkname)

    else:
        breakpoint()
        print(member.name)


def main():
    version = latest_lts_version()
    saved_tarball = Path(f'~/Software/node-{version}-linux-x64.tar.xz').expanduser()
    if not saved_tarball.exists():
        save_tarball(FETCH_URL.format(version=version), saved_tarball)

    archive = tarfile.open(saved_tarball)
    unpacked_root = Path(f'~/Software/node-{version}-linux-x64').expanduser()
    root_tar_dir = f'node-{version}-linux-x64'

    for member in archive:
        save_member(archive, unpacked_root, member, root_tar_dir)

    symlink = Path('~/Software/node-linux-x64').expanduser()
    if symlink.exists():
        symlink.unlink()
    symlink.symlink_to(unpacked_root)


if __name__ == '__main__':
    main()
