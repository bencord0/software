#!/usr/bin/env python
import os
import re
import requests
import shutil
import tarfile
from pathlib import Path
from tqdm import tqdm
from urllib.parse import urlparse

INDEX_URL = 'https://api.github.com/repos/circleci-public/circleci-cli/releases'
FETCH_URL = 'https://github.com/circleci-public/circleci-cli/releases/download/v{version}/circleci-cli_{version}_linux_amd64.tar.gz'
SAVED_TARBALL = '~/Software/circleci-cli_{version}_linux_amd64.tar.gz'
UNPACKED_ROOT = '~/Software/circleci-cli_{version}'
TAR_PREFIX = 'circleci-cli_{version}_linux_amd64'
SYMLINK_PATH = '~/Software/circleci-cli'


def latest_version():
    index = requests.get(INDEX_URL).json()

    latest_version = index[0]['name']

    return latest_version[1:]


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
        breakpoint()
        content = archive.extractfile(member)

        # Set file content
        buf = content.read()
        path.parent.mkdir()
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

    saved_tarball = Path(SAVED_TARBALL.format(version=version)).expanduser()
    if not saved_tarball.exists():
        save_tarball(fetch_url, saved_tarball)

    archive = tarfile.open(saved_tarball)
    unpacked_root = Path(UNPACKED_ROOT.format(version=version)).expanduser()

    member_path = Path(TAR_PREFIX.format(version=version)) / 'circleci'
    member = archive.getmember(str(member_path))
    save_member(archive, unpacked_root, member, TAR_PREFIX.format(version=version))

    breakpoint()
    symlink = Path(SYMLINK_PATH).expanduser()
    if symlink.exists():
        symlink.unlink()
    symlink.symlink_to(unpacked_root)

if __name__ == '__main__':
    main()
