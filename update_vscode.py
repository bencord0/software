#!/usr/bin/env python
import os
import re
import requests
import tarfile
from pathlib import Path
from tqdm import tqdm
from urllib.parse import urlparse

URL = 'https://code.visualstudio.com/sha/download?build=stable&os=linux-x64'


class LocationParser:
    def __init__(self, url: str):
        self.url = url
        self.parsed_url = urlparse(url)
        self.path = Path(self.parsed_url.path)

        # 'code-stable-x64-xxxxxxxx.tar.gz
        self.name = self.path.name
        self.version = re.fullmatch(
            'code-stable-x64-(?P<version>\d+).tar.gz',
            self.name,
        )['version']


def main():
    redirect = requests.get(URL, allow_redirects=False)

    location = LocationParser(redirect.headers['location'])
    version = location.version

    saved_tarball = Path(f'~/Software/code-{version}.tar.gz').expanduser()
    if not saved_tarball.exists():
        save_tarball(location.url, saved_tarball)

    archive = tarfile.open(saved_tarball)
    unpacked_root = Path(f'~/Software/VSCode-linux-x64-{version}').expanduser()

    for member in archive:
        save_member(archive, unpacked_root, member)

    symlink = Path('~/Software/VSCode-linux-x64').expanduser()
    if symlink.exists():
        symlink.unlink()
    symlink.symlink_to(unpacked_root)


def save_tarball(url, path):
    with path.open('wb') as tarball:
        print(f'Downloading: {url}')
        download = requests.get(url, stream=True)
        content_length = int(download.headers['content-length'])

        with tqdm(total=content_length) as progress:
            for chunk in download.iter_content(chunk_size=4096):
                progress.update(len(chunk))
                tarball.write(chunk)


def save_member(archive, root, member):
    path = Path(
        member.name.replace('VSCode-linux-x64', str(root))
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

    else:
        breakpoint()
        print(member.name)


if __name__ == '__main__':
    main()
