import fire
import mutagen
import urllib.request
import json
import os
from pprint import pprint
import glob
import sys
import re
from functools import reduce
from discogs_tag import __NAME__, __VERSION__

SKIP_KEYS = [
  'artist',
  'composer',
  'title',
  'position',
  'date',
  'subtrack',
  'album',
  'genre',
  'albumartist'
]

AUDIO_EXTENSIONS = ['flac', 'mp3']

def tag(
  release,
  dir='./',
  dry=False,
  ignore=False,
  skip=None
):
  """Tag the audio files with the given Discogs release.

  The skip flag can take one or more of the following values, comma-separated:
      artist, composer, title, position, date, subtrack, album, genre, albumartist

  """
  options = parse_options(locals())
  request = urllib.request.Request(f'https://api.discogs.com/releases/{release}', headers = {
    'User-Agent': f'{__NAME__} {__VERSION__}'
  })
  with urllib.request.urlopen(request) as response:
    data = json.load(response)
    files = get_files(dir)
    apply_metadata(data, files, options)

def copy(
  src,
  dir='./',
  dry=False,
  ignore=False,
  skip=None
):
  """Copy the audio tags from source to destination folders.

  The skip flag can take one or more of the following values, comma-separated:
      artist, composer, title, position, date, subtrack, album, genre, albumartist

  """
  options = parse_options(locals())
  src_files = get_files(src)
  if not src_files:
    raise Exception(f'No source files found at {src}. Aborting.')

  data = read_metadata(src_files, options)
  dst_files = get_files(dir)
  if options['dry']:
    pprint(data)
  else:
    apply_metadata(data, dst_files, options)

def read_metadata(files, options):
  """Read metadata from OS audio files and return data structure that mimics Discogs release."""
  def safe_position(audio, n):
    try:
      return audio['tracknumber'][0].split('/')[0].lstrip('0')
    except:
      return str(n)
  def safe_year(audio):
    try:
      return int(audio['date'][0].split('-')[0])
    except:
      return None

  tracklist = []
  for n, file in enumerate(files):
    audio = mutagen.File(file, easy=True)
    tracklist.append({
      'type_': 'track',
      'position': safe_position(audio, n+1),
      'artists': [{ 'anv': artist } for artist in audio.get('artist', [])],
      'title': audio.get('title', [''])[0],
      'extraartists': [{
        'role': 'Written-By',
        'anv': composer
      } for composer in audio.get('composer', [])]
    })
  return {
    'artists': [{ 'anv': artist } for artist in audio.get('albumartist', [])],
    'title': audio.get('album', [''])[0],
    'year': safe_year(audio),
    'genres': audio.get('genre', []),
    'tracklist': sorted(tracklist, key=lambda track: int(track['position']))
  }

def apply_metadata(release, files, options):
  """Apply Discogs release metadada to OS audio files."""
  def get_tracks(tracklist):
    def reduce_track(tracks, track):
      if track['type_'] == 'track':
        tracks.append(track)
      if not options['skip_subtrack'] and 'sub_tracks' in track:
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
      merge_metadata(release, track, audio, options)
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

def get_files(dir):
  return sorted(reduce(lambda xs, ys: xs + ys, [
    glob.glob(os.path.join(glob.escape(dir), '**', f"*.{ext}"), recursive=True) for ext in AUDIO_EXTENSIONS
  ]))

def parse_options(options):
  for skip in SKIP_KEYS:
    options['skip_' + skip] = False
  if options['skip'] is not None:
    for skip in options['skip'].lower():
      options['skip_' + skip] = True
  return options

def merge_metadata(release, track, audio, options):
  def artist_name(artist):
    name = None
    if 'anv' in artist and artist['anv']:
      name = artist['anv']
    elif 'name' in artist and artist['name']:
      name = artist['name']
    return re.sub(r"\s+\(\d+\)$", '', name) if name else None

  if not options['skip_title']:
    audio['title'] = track['title']

  if not options['skip_artist']:
    artists = []
    if 'artists' in track:
      artists += [artist_name(artist) for artist in track['artists']]
    if 'extraartists' in track:
      artists += [artist_name(artist) for artist in filter(lambda a: a['role'].casefold() != 'Written-By'.casefold(), track['extraartists'])]
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

  if not options['skip_composer']:
    composers = [artist_name(composer) for composer in filter(lambda a: a['role'].casefold() == 'Written-By'.casefold(), track['extraartists'])] if 'extraartists' in track else None
    if composers:
      audio['composer'] = ', '.join(composers)

  if not options['skip_position']:
    positions = track['position'].split('-')
    audio['tracknumber'] = positions[-1]
    if len(positions) > 1:
      audio['discnumber'] = positions[0]

  if not options['skip_date']:
    if 'year' in release and release['year']:
      audio['date'] = str(release['year'])

def cli():
  fire.Fire({
    'tag': tag,
    'copy': copy,
  })
