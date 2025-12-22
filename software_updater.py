import requests
import tarfile
import os

from pathlib import Path
from tqdm import tqdm

def save_tarball(url: str, path: Path):
    with path.open('wb') as tarball:
        print(f'Downloading: {url}')

        download = requests.get(url, stream=True)
        content_length = int(download.headers['content-length'])

        with tqdm(total=content_length) as progress:
            for chunk in download.iter_content(chunk_size=4096):
                progress.update(len(chunk))
                tarball.write(chunk)

def save_zipball(url: str, path: Path):
    return save_tarball(url, path)


def unpack_tarball(tarball: Path, root: Path, prefix: str):
    archive = tarfile.open(tarball)
    for member in archive:
        path = Path(member.name)
        if prefix:
            path = Path(member.name.replace(prefix, str(root)))
        print(f'{str(path)}')

        if member.isdir():
            if not path.exists():
                path.mkdir()

        elif member.isfile():
            content = archive.extractfile(member)

            # Reads into memory, then into a file.
            path.write_bytes(content.read())

            # Set attributes
            path.chmod(member.mode)

            # Set timestamps
            os.utime(path, (member.mtime, member.mtime))





