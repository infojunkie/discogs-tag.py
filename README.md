discogs-tag
===========

An audio tagger based on Discogs metadata.

# Installation
- Install [`poetry`](https://python-poetry.org/docs/#installation)
- `poetry install && poetry build && pip install .`

# Usage
```shell
NAME
    discogs-tag

SYNOPSIS
    discogs-tag COMMAND

COMMANDS
    COMMAND is one of the following:

     tag
       Tag the audio files with the given Discogs release.

     copy
       Copy the audio tags from source to destination folders.

     rename
       Rename the audio files based on the given format string.
```
## tag
```shell
NAME
    discogs-tag tag - Tag the audio files with the given Discogs release.

SYNOPSIS
    discogs-tag tag RELEASE <flags>

DESCRIPTION
    The RELEASE can be one of the following:
        - A full Discogs release URL, e.g. https://www.discogs.com/release/16215626-Pink-Floyd-Wish-You-Were-Here
        - The numeric portion of the above, e.g. 16215626
        - A local file URI pointing to a release JSON file

    The SKIP flag can take one or more of the following values, comma-separated:
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
## copy
```shell
NAME
    discogs-tag copy - Copy the audio tags from source to destination folders.

SYNOPSIS
    discogs-tag copy SRC <flags>

DESCRIPTION
    The SKIP flag can take one or more of the following values, comma-separated:
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
## rename
```shell
NAME
    discogs-tag rename - Rename the audio files based on the given format string.

SYNOPSIS
    discogs-tag rename FORMAT <flags>

DESCRIPTION
    The FORMAT string specifies how to rename the audio files and/or directories according to the following tags:
        %a Artist
        %z Album artist
        %b Album title
        %p Composer
        %d Disc nummber
        %g Genre
        %n Track number
        %t Track title
        %y Year
        /  Directory separator: Specifies subdirectories to be created starting from the given directory.
           Non-audio files will be moved to their existing subdirectories within the destination root which is assumed to be unique.

POSITIONAL ARGUMENTS
    FORMAT

FLAGS
    --dir=DIR
        Default: './'
    --dry=DRY
        Default: False
    -i, --ignore=IGNORE
        Default: False

NOTES
    You can also use flags syntax for POSITIONAL ARGUMENTS
```
