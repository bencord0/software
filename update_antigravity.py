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

from software_updater import save_and_symlink

INDEX_URL = 'https://antigravity.google/download/linux'
SAVED_TARBALL = '~/Software/Antigravity-{version}.tar.gz'
UNPACKED_ROOT = '~/Software/Antigravity-{version}'
SYMLINK_PATH = '~/Software/Antigravity'
PREFIX = 'Antigravity'

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
    save_and_symlink(url, SAVED_TARBALL, UNPACKED_ROOT, SYMLINK_PATH, version, PREFIX)

if __name__ == '__main__':
    main()
