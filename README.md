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
    Tag the audio files with the given Discogs release.

POSITIONAL ARGUMENTS
    RELEASE

FLAGS
    --dir=DIR
        Default: './'
    --dry=DRY
        Default: False
    -i, --ignore=IGNORE
        Default: False
    --skip_artist=SKIP_ARTIST
        Default: False
    --skip_title=SKIP_TITLE
        Default: False
    --skip_composer=SKIP_COMPOSER
        Default: False
    --skip_position=SKIP_POSITION
        Default: False
    --skip_year=SKIP_YEAR
        Default: False
    --skip_subtrack=SKIP_SUBTRACK
        Default: False

NOTES
    You can also use flags syntax for POSITIONAL ARGUMENTS
```
```shell
NAME
    discogs-tag copy - Copy the audio tags from source to destination folders.

SYNOPSIS
    discogs-tag copy SRC <flags>

DESCRIPTION
    Copy the audio tags from source to destination folders.

POSITIONAL ARGUMENTS
    SRC

FLAGS
    --dir=DIR
        Default: './'
    --dry=DRY
        Default: False
    -i, --ignore=IGNORE
        Default: False
    --skip_artist=SKIP_ARTIST
        Default: False
    --skip_title=SKIP_TITLE
        Default: False
    --skip_composer=SKIP_COMPOSER
        Default: False
    --skip_position=SKIP_POSITION
        Default: False
    --skip_year=SKIP_YEAR
        Default: False
    --skip_subtrack=SKIP_SUBTRACK
        Default: False

NOTES
    You can also use flags syntax for POSITIONAL ARGUMENTS
```
