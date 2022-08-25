#!/usr/bin/env python
import os
import re
import hashlib
import requests
from pathlib import Path
from tqdm import tqdm
from urllib.parse import urlparse

# INDEX_URL = 'https://dl.k8s.io/release/stable.txt' # 302 redirect
INDEX_URL = 'https://storage.googleapis.com/kubernetes-release/release/stable.txt'
FETCH_BINARY_URL = 'https://dl.k8s.io/release/{version}/bin/linux/amd64/{binary}'
FETCH_CHECKSUM_URL = 'https://dl.k8s.io/release/{version}/bin/linux/amd64/{binary}.sha256'


def latest_version():
    latest_version = requests.get(INDEX_URL).text
    return latest_version


def save_binary(root, version, binary):
    print(f'{binary}-{version}: Fetching checksum')
    checksum = requests.get(
        FETCH_CHECKSUM_URL.format(version=version, binary=binary)
    ).text
    print(f'{binary}-{version}: {checksum}')

    download = requests.get(
        FETCH_BINARY_URL.format(version=version, binary=binary),
        stream=True,
    )
    content_length = int(download.headers['content-length'])

    hasher = hashlib.sha256()
    path = root / f'{binary}-{version}'
    with path.open('wb') as saved_content:
        with tqdm(total=content_length) as progress:
            for chunk in download.iter_content(chunk_size=4096):
                progress.update(len(chunk))
                hasher.update(chunk)
                saved_content.write(chunk)

    digest = hasher.hexdigest()
    if checksum != digest:
        print(f'Checksum mismatch: {digest}')
        path.unlink()
        return

    # Set execute bits on binaries
    path.chmod(0o755)


def main():
    version = latest_version()
    binaries = ('kubectl', )

    root = Path(f'~/Software/kubernetes/bin').expanduser()
    if not root.exists():
        root.mkdir(parents=True)

    for binary in binaries:
        print(f'Fetching: {binary}')
        save_binary(root, version, binary)

        symlink = root / binary
        target = root / f'{binary}-{version}'

        if not target.exists():
            continue

        if symlink.exists():
            symlink.unlink()
        symlink.symlink_to(target)

    # sudo setcap cap_net_bind_service+eip $(readlink -ef $(which kubectl))

if __name__ == '__main__':
    main()
