import fire
import mutagen
import urllib.request
import json
import os
from pprint import pprint
import glob
import sys
import re
from discogs_tag import __NAME__, __VERSION__

def tag(
  release,
  dir='./',
  dry=False,
  ignore=False,
  skip_artist=False,
  skip_title=False,
  skip_composer=False,
  skip_position=False,
  skip_year=False
):
  """Tag the audio files with the given Discogs release."""
  options = locals()
  request = urllib.request.Request(f'https://api.discogs.com/releases/{release}', headers = {
    'User-Agent': f'{__NAME__} {__VERSION__}'
  })
  with urllib.request.urlopen(request) as response:
    data = json.load(response)
    files = sorted(
      glob.glob(os.path.join(glob.escape(dir), '**', '*.flac'), recursive=True) +
      glob.glob(os.path.join(glob.escape(dir), '**', '*.mp3'), recursive=True)
    )
    apply_metadata(data, files, options)

def apply_metadata(release, files, options):
  tracks = list(filter(lambda t: t['type_'] == 'track', release['tracklist']))
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

def merge_metadata(release, track, audio, options):
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

  if not options['skip_composer']:
    composers = [artist_name(composer) for composer in filter(lambda a: a['role'].casefold() == 'Written-By'.casefold(), track['extraartists'])] if 'extraartists' in track else None
    if composers:
      audio['composer'] = ', '.join(composers)

  if not options['skip_position']:
    positions = track['position'].split('-')
    audio['tracknumber'] = positions[-1]
    if len(positions) > 1:
      audio['discnumber'] = positions[0]

  if not options['skip_year']:
    if 'year' in release and release['year']:
      audio['date'] = str(release['year'])

def artist_name(artist):
  name = None
  if 'anv' in artist and artist['anv']:
    name = artist['anv']
  elif 'name' in artist and artist['name']:
    name = artist['name']
  return re.sub(r"\s+\(\d+\)$", '', name) if name else None

def cli():
  fire.Fire(tag)
