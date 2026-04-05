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
        if prefix:
            path = root / member.name.removeprefix(prefix).removeprefix('/')
        else:
            path = root / member.name
        print(f'{str(path)}')

        if member.isdir():
            if not path.exists():
                path.mkdir(parents=True)

        elif member.isfile():
            content = archive.extractfile(member)

            # Reads into memory, then into a file.
            buf = content.read()
            path.write_bytes(buf)

            # Set attributes
            path.chmod(member.mode)

            # Set timestamps
            os.utime(path, (member.mtime, member.mtime))

        elif member.issym():
            path.symlink_to(member.linkname)


def save_and_symlink(url, tarball, root, symlink, version, prefix):
    saved_tarball = Path(tarball.format(version=version)).expanduser()
    if not saved_tarball.exists():
        save_tarball(url.format(version=version), saved_tarball)

    unpacked_root = Path(root.format(version=version)).expanduser()
    unpack_tarball(saved_tarball, unpacked_root, prefix)

    symlink = Path(symlink).expanduser()
    if symlink.exists():
        symlink.unlink()
    symlink.symlink_to(unpacked_root)
