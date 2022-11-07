class SemVer():
    def __init__(self, version):
        major, minor, patch = version.split('.', 3)

        self._hash = hash(version)
        self._major = int(major.removeprefix('v'))
        self._minor = int(minor)
        self._patch = int(patch)

    def __hash__(self):
        return self._hash

    def __repr__(self):
        return f'<SemVer {self.version}>'

    @property
    def version(self):
        return f'{self._major}.{self._minor}.{self._patch}'

    def __eq__(self, other):
        return (
            self._major == other._major
            and self._minor == other._minor
            and self._patch == other._patch
        )

    def __gt__(self, other):
        if self.__eq__(other):
            return False

        return (
            self._major > other._major
            or (self._major >= other._major and self._minor > other._minor)
            or (self._major >= other._major and self._minor >= other._minor and self._patch > other._patch)
        )
