#!/usr/bin/env python
#
# Needs:
# - dev-python/selenium
# - dev-util/selenium-manager
# - net-misc/geckodriver
import re

from os.path import expanduser
from bs4 import BeautifulSoup
from selenium.webdriver import Firefox, FirefoxOptions
from pathlib import Path

from software_updater import save_tarball, unpack_tarball

INDEX_URL = 'https://antigravity.google/download/linux'
SAVED_TARBALL = '~/Software/Antigravity-{version}.tar.gz'
UNPACKED_ROOT = '~/Software/Antigravity-{version}'
SYMLINK_PATH = '~/Software/Antigravity'

VersionMatch = re.compile(r'.*/stable/(?P<version>.+)/linux-x64/Antigravity.tar.gz$')

options = FirefoxOptions()
options.add_argument('--headless')

# Custom location of firefox nightly
options.binary_location = expanduser('~/firefox/firefox')


def find_latest():
    browser = Firefox(options=options)

    try:
        browser.get(INDEX_URL)
        source = BeautifulSoup(browser.page_source, 'lxml')

        links = []
        for link in source.find_all('a'):
            if url := link.get('href'):
                links.append(url)

        (download_link,) = [l for l in links if l.endswith('Antigravity.tar.gz')]
        version = VersionMatch.match(download_link).group('version')
    finally:
        browser.quit()

    return download_link, version


def main():
    url, version = find_latest()
    saved_tarball = Path(SAVED_TARBALL.format(version=version)).expanduser()
    if not saved_tarball.exists():
        save_tarball(url, saved_tarball)

    unpacked_root = Path(UNPACKED_ROOT.format(version=version)).expanduser()
    unpack_tarball(saved_tarball, unpacked_root, prefix='Antigravity')

    symlink = Path(SYMLINK_PATH).expanduser()
    if symlink.exists():
        symlink.unlink()
    symlink.symlink_to(unpacked_root)

if __name__ == '__main__':
    main()
