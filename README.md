discogs-tag
===========

A rudimentary audio tagger based on Discogs metadata.

# Installation
- Install [`poetry`](https://python-poetry.org/docs/#installation)
- `poetry install && poetry build && pip install .`

# Usage
```shell
NAME
    discogs-tag tag - Tag the audio files with the given Discogs release.

SYNOPSIS
    discogs-tag tag RELEASE <flags>

DESCRIPTION
    The skip flag can take one or more of the following values, comma-separated:
        artist, composer, title, position, date, subtrack, album, genre, albumartist

POSITIONAL ARGUMENTS
    RELEASE

FLAGS
    --dir=DIR
        Default: './'
    --dry=DRY
        Default: False
    -i, --ignore=IGNORE
        Default: False
    -s, --skip=SKIP
        Type: Optional[]
        Default: None

NOTES
    You can also use flags syntax for POSITIONAL ARGUMENTS
```
```shell
NAME
    discogs-tag copy - Copy the audio tags from source to destination folders.

SYNOPSIS
    discogs-tag copy SRC <flags>

DESCRIPTION
    The skip flag can take one or more of the following values, comma-separated:
        artist, composer, title, position, date, subtrack, album, genre, albumartist

POSITIONAL ARGUMENTS
    SRC

FLAGS
    --dir=DIR
        Default: './'
    --dry=DRY
        Default: False
    -i, --ignore=IGNORE
        Default: False
    -s, --skip=SKIP
        Type: Optional[]
        Default: None

NOTES
    You can also use flags syntax for POSITIONAL ARGUMENTS
```
