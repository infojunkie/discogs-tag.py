import fire
import mutagen
import urllib.request
import json
import os
import glob
import sys
import regex as re
from urllib.parse import urlparse
from pprint import pprint
from functools import reduce
from contextlib import suppress
from pathvalidate import sanitize_filename
from discogs_tag import __NAME__, __VERSION__

SKIP_KEYS = [
  'artist',
  'composer',
  'title',
  'position',
  'date',
  'subtracks',
  'album',
  'genre',
  'albumartist'
]

COMPOSER_TAGS = [
  'Written-By',
  'Composed By'
]

VARIOUS_ARTISTS = 'Various Artists'

AUDIO_EXTENSIONS = ['flac', 'mp3']

def version():
  """ Return version information. """
  print(json.dumps({
    'name': __NAME__,
    'version': __VERSION__
  }, indent=4))

def tag(
  release,
  dir='./',
  dry=False,
  ignore=False,
  skip=None,
  only=None
):
  """Tag the audio files with the given Discogs release.

  The RELEASE can be one of the following:
      - A full Discogs release URL, e.g. https://www.discogs.com/release/16215626-Pink-Floyd-Wish-You-Were-Here
      - The numeric portion of the above, e.g. 16215626
      - A local file URI pointing to a release JSON file

  The SKIP and ONLY flags can take one or more of the following values, comma-separated:
      artist, composer, title, position, date, subtracks, album, genre, albumartist

      If subtracks are skipped, subtrack titles get appended to their parent track.

  """
  options = parse_options(locals())
  response = get_release(release)
  data = json.load(response)
  files = list_files(dir)
  apply_metadata(data, files, options)

def copy(
  src,
  dir='./',
  dry=False,
  ignore=False,
  skip=None,
  only=None
):
  """Copy the audio tags from source to destination folders.

  The SKIP and ONLY flags can take one or more of the following values, comma-separated:
      artist, composer, title, position, date, subtracks, album, genre, albumartist

      If subtracks are skipped, subtrack titles get appended to their parent track.

  """
  options = parse_options(locals())
  src_files = list_files(src)
  if not src_files:
    raise Exception(f'No source files found at {src}. Aborting.')

  audios = [mutagen.File(file, easy=True) for file in src_files]
  data = read_metadata(audios, options)
  dst_files = list_files(dir)
  if options['dry']:
    pprint(data)
  else:
    apply_metadata(data, dst_files, options)

def rename(
  format,
  dir='./',
  dry=False,
  ignore=False
):
  """Rename the audio files based on the given format string.

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

  """
  options = parse_options(locals())
  src_root = os.path.realpath(dir)
  if not os.path.exists(src_root):
    raise Exception(f'Directory "{dir}" not found. Aborting.')
  files = list_files(src_root)
  if not files:
    raise Exception(f'Directory "{dir}" has no audio files. Aborting.')

  # Extract and create destination root from first audio file.
  audio = mutagen.File(files[0], easy=True)
  _, dst_root = rename_path(src_root, audio, format, options)

  # Iterate on all files and directories to move them to the destination.
  # - Audio files are renamed according to their format, including subfolder structure
  # - Other files are moved to the same subfolder in the destination tree
  # - Folders are recreated on the destination and removed from the source if empty
  for dirpath, dirnames, filenames in os.walk(src_root, topdown=False):
    for filename in filenames:
      src_filepath = os.path.join(dirpath, filename)
      _, ext = os.path.splitext(src_filepath)
      if ext[1:] in AUDIO_EXTENSIONS:
        audio = mutagen.File(src_filepath, easy=True)
        dst_path, _ = rename_path(src_root, audio, format, options)
        rename_file(src_filepath, dst_path, audio, format, options)
      else:
        dst_filepath = os.path.join(dst_root, os.path.relpath(src_filepath, src_root))
        if options['dry']:
          print("%s => %s" % (src_filepath, dst_filepath))
        else:
          os.makedirs(os.path.dirname(dst_filepath), exist_ok=True)
          os.rename(src_filepath, dst_filepath)
    for dirname in dirnames:
      src_path = os.path.join(dirpath, dirname)
      if options['dry']:
        print("✗ %s" % (src_path))
      else:
        with suppress(OSError):
          os.rmdir(src_path)

  # Also delete source root.
  if options['dry']:
    print("✗ %s" % (src_root))
  else:
    with suppress(OSError):
      os.rmdir(src_root)

def get_release(release):
  """ Get release JSON from Discogs URL, file URI or Discogs release number. """
  headers = {
    'User-Agent': f'{__NAME__} {__VERSION__}'
  }
  match = re.match(r"https://www\.discogs\.com/release/(\d*)", release)
  if match:
    release = f'https://api.discogs.com/releases/{match.group(1)}'
  try:
    request = urllib.request.Request(release, headers=headers)
    return urllib.request.urlopen(request)
  except Exception:
    request = urllib.request.Request(f'https://api.discogs.com/releases/{release}', headers=headers)
    return urllib.request.urlopen(request)

def read_metadata(audios, options):
  """Read metadata from audio files and return data structure that mimics Discogs release."""
  def safe_position(audio, n):
    try:
      tracknumber = audio.get('tracknumber', [str(n)])[0].split('/')
      discnumber = audio.get('discnumber')
      if discnumber:
        return discnumber[0].lstrip('0') + '-' + tracknumber[0].lstrip('0')
      else:
        return tracknumber[0].lstrip('0')
    except:
      return str(n)

  def safe_year(audio):
    try:
      return int(audio['date'][0].split('-')[0])
    except:
      return None

  tracklist = []
  for n, audio in enumerate(audios):
    tracklist.append({
      'type_': 'track',
      'position': safe_position(audio, n+1),
      'artists': [{ 'anv': artist } for artist in audio.get('artist', [])],
      'title': audio.get('title', [''])[0],
      'extraartists': [{
        'role': 'Composed By',
        'anv': composer
      } for composer in audio.get('composer', [])]
    })
  return {
    'artists': [{ 'anv': artist } for artist in audio.get('albumartist', [])],
    'title': audio.get('album', [''])[0],
    'year': safe_year(audio),
    'genres': audio.get('genre', []),
    'tracklist': sorted(tracklist, key=lambda track: int(track['position'].split('-')[0]))
  }

def apply_metadata(release, files, options):
  """Apply Discogs release metadada to audio files."""
  def get_tracks(tracklist):
    def reduce_track(tracks, track):
      if track['type_'] == 'track':
        tracks.append(track)
      elif options['skip_subtracks'] and 'sub_tracks' in track:
        tracks.append(track)
      if not options['skip_subtracks'] and 'sub_tracks' in track:
        tracks = tracks + get_tracks(track['sub_tracks'])
      return tracks
    return reduce(reduce_track, tracklist, [])

  tracks = get_tracks(release['tracklist'])
  if len(files) != len(tracks):
    if options['ignore']:
      print(f'Expecting {len(tracks)} files but found {len(files)}. Ignoring.', file=sys.stderr)
    else:
      raise Exception(f'Expecting {len(tracks)} files but found {len(files)}. Aborting.')

  for n, track in enumerate(tracks):
    try:
      audio = mutagen.File(files[n], easy=True)
      audio = apply_metadata_track(release, track, audio, n+1, options)
      if options['dry']:
        pprint(audio)
      else:
        audio.save()
    except Exception as e:
      if options['ignore']:
        print(e, file=sys.stderr)
      else:
        raise e

  if not options['dry']:
    print(f'Processed {len(files)} audio files.')

def rename_component(audio, format, options):
  """ Rename a path component based on format string with tags from the audio metadata. """
  tags = {
    '%a': (lambda audio: audio.get('artist', [''])[0]),
    '%z': (lambda audio: audio.get('albumartist', [''])[0]),
    '%b': (lambda audio: audio.get('album', [''])[0]),
    '%p': (lambda audio: audio.get('composer', [''])[0]),
    '%d': (lambda audio: audio.get('discnumber', [''])[0]),
    '%g': (lambda audio: audio.get('genre', [''])[0]),
    '%n': (lambda audio: '%02d' % int(audio.get('tracknumber', [0])[0])),
    '%t': (lambda audio: audio.get('title', [''])[0]),
    '%y': (lambda audio: audio.get('date', [''])[0])
  }

  # First, remove from format string all empty tags and neighbouring characters.
  for tag, fn in tags.items():
    if tag in format:
      try:
        replace = fn(audio).strip()
        # If replacement is empty, also remove format chars until next tag.
        if not replace:
          format = re.sub(r"\p{Ps}?" + re.escape(tag) + r"[^%]*", '', format)
      except Exception as e:
        if options['ignore']:
          print(e, file=sys.stderr)
        else:
          raise e

  # Now replace tags with metadata values.
  component = format
  for tag, fn in tags.items():
    if tag in format:
      try:
        replace = fn(audio).strip()
        component = component.replace(tag, replace)
      except Exception as e:
        pass

  return component

def rename_path(src_root, audio, format, options):
  """ Create directory path based on format string with tags from the audio metadata. """
  # Expand tags in each path component.
  paths = []
  for dir in format.split('/')[:-1]:
    paths.append(sanitize_filename(rename_component(audio, dir, options), replacement_text='-'))
  if not paths:
    return src_root, src_root

  # Create the new path.
  dst_path = os.path.join(os.path.dirname(os.path.realpath(src_root)), *paths)
  if not options['dry']:
    os.makedirs(dst_path, exist_ok=True)

  return dst_path, os.path.join(os.path.dirname(os.path.realpath(src_root)), paths[0])

def rename_file(src_file, dst_path, audio, format, options):
  """ Rename audio file based on format string with tags from the audio metadata. """
  # Get the last component of the format path.
  filename = format.split('/')[-1].strip()

  if len(filename) == 0:
    # No format specified: Keep the original filename
    filename = os.path.basename(src_file)
  else:
    # Replace tags in the filename with audio metadata.
    filename = rename_component(audio, filename, options)

    # Add back the original file extension.
    _, ext = os.path.splitext(src_file)
    filename += ext

    # Sanitize the filename.
    filename = sanitize_filename(filename, replacement_text='-')

  # Add the original path.
  dst_file = os.path.join(dst_path, filename)
  if options['dry']:
    print("%s => %s" % (src_file, dst_file))
  else:
    os.rename(src_file, dst_file)

  return dst_file

def list_files(dir):
  return sorted(reduce(lambda xs, ys: xs + ys, [
    glob.glob(os.path.join(glob.escape(dir), '**', f"*.{ext}"), recursive=True) for ext in AUDIO_EXTENSIONS
  ]))

def parse_options(options):
  for skip in SKIP_KEYS:
    options['skip_' + skip.lower()] = False
  if 'skip' in options and options['skip'] is not None:
    if isinstance(options['skip'], str):
      options['skip'] = [options['skip']]
    for skip in options['skip']:
      options['skip_' + skip.lower()] = True
  if 'only' in options and options['only'] is not None:
    for skip in SKIP_KEYS:
      options['skip_' + skip.lower()] = True
    if isinstance(options['only'], str):
      options['only'] = [options['only']]
    for skip in options['only']:
      options['skip_' + skip.lower()] = False
  return options

def apply_metadata_track(release, track, audio, n, options):
  def artist_name(artist):
    name = None
    if 'anv' in artist and artist['anv']:
      name = artist['anv']
    elif 'name' in artist and artist['name']:
      name = artist['name']
    if name:
      name = re.sub(r"^Various$", VARIOUS_ARTISTS, name, flags=re.IGNORECASE)
      name = re.sub(r"\s+\(\d+\)$", '', name)
    return name

  if not options['skip_title']:
    title = track['title']
    if options['skip_subtracks'] and 'sub_tracks' in track:
      title += ': ' + ' / '.join([subtrack['title'] for subtrack in track['sub_tracks'] if subtrack['type_'] == 'track'])
    if title:
      audio['title'] = title

  if not options['skip_artist']:
    artists = []
    if 'artists' in track:
      artists += [artist_name(artist) for artist in track['artists']]
    if not artists:
      artists += [artist_name(artist) for artist in release['artists']]
    if artists:
      audio['artist'] = ', '.join(artists)

  if not options['skip_albumartist']:
    artists = []
    if 'artists' in release:
      artists += [artist_name(artist) for artist in release['artists']]
    if artists:
      audio['albumartist'] = ', '.join(artists)

  if not options['skip_genre']:
    genres = []
    if 'genres' in release:
      genres += [genre for genre in release['genres']]
    if 'styles' in release:
      genres += [genre for genre in release['styles']]
    if genres:
      audio['genre'] = ', '.join(genres)

  if not options['skip_album']:
    if 'title' in release:
      audio['album'] = release['title']

  if not options['skip_composer'] and 'extraartists' in track:
    composers = [artist_name(composer) for composer in track['extraartists'] if composer['role'].casefold() in [c.casefold() for c in COMPOSER_TAGS]]
    if composers:
      audio['composer'] = ', '.join(composers)

  if not options['skip_position']:
    positions = track['position'].split('-')
    audio['tracknumber'] = positions[-1] or str(n)
    if len(positions) > 1:
      audio['discnumber'] = positions[0]

  if not options['skip_date'] and 'year' in release:
    audio['date'] = str(release['year'])

  return audio

def cli():
  fire.Fire({
    'version': version,
    'tag': tag,
    'copy': copy,
    'rename': rename
  })
