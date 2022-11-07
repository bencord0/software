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
        buf = content.read()
        if not path.parent.exists():
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

    for member in archive:
        save_member(archive, unpacked_root, member, SOFTWARE_PREFIX)
    breakpoint()

    symlink = Path(SYMLINK_PATH).expanduser()
    breakpoint()
    if symlink.exists():
        symlink.unlink()
    symlink.symlink_to(unpacked_root)

if __name__ == '__main__':
    main()
