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

def tag(release, dir = './', dry = False, ignore = False):
  """Tag the audio files in dir with the given Discogs release."""
  request = urllib.request.Request(f'https://api.discogs.com/releases/{release}', headers = {
    'User-Agent': f'{__NAME__} {__VERSION__}'
  })
  with urllib.request.urlopen(request) as response:
    data = json.load(response)
    files = sorted(
      glob.glob(os.path.join(glob.escape(dir), '**', '*.flac'), recursive=True) +
      glob.glob(os.path.join(glob.escape(dir), '**', '*.mp3'), recursive=True)
    )
    apply_metadata(data, files, dry, ignore)

def apply_metadata(data, files, dry, ignore):
  tracks = list(filter(lambda t: t['type_'] == 'track', data['tracklist']))
  if (len(files) != len(tracks)):
    if (not ignore):
      raise Exception(f'Expecting {len(tracks)} files but found {len(files)}. Aborting.')
    else:
      print(f'Expecting {len(tracks)} files but found {len(files)}. Ignoring.', file=sys.stderr)

  for n, track in enumerate(tracks):
    try:
      audio = mutagen.File(files[n], easy=True)
      merge_metadata(track, audio)
      if (dry):
        pprint(audio)
      else:
        audio.save()
    except Exception as e:
      if (not ignore):
        raise e
      else:
        print(e, file=sys.stderr)

  if (not dry):
    print(f'Processed {len(files)} audio files.')

def merge_metadata(track, audio):
  audio['title'] = track['title']
  artists = []
  if 'artists' in track:
    artists += [artist_name(artist) for artist in track['artists']]
  if 'extraartists' in track:
    artists += [artist_name(artist) for artist in filter(lambda a: a['role'].casefold() != 'Written-By'.casefold(), track['extraartists'])]
  if (artists):
    audio['artist'] = ', '.join(artists)
  positions = track['position'].split('-')
  audio['tracknumber'] = positions[-1]
  if (len(positions) > 1):
    audio['discnumber'] = positions[0]
  composers = [artist_name(composer) for composer in filter(lambda a: a['role'].casefold() == 'Written-By'.casefold(), track['extraartists'])] if 'extraartists' in track else None
  if (composers):
    audio['composer'] = ', '.join(composers)

def artist_name(artist):
  name = None
  if 'anv' in artist and artist['anv']:
    name = artist['anv']
  elif 'name' in artist and artist['name']:
    name = artist['name']
  return re.sub(r"\s+\(\d+\)$", '', name) if name else None

def cli():
  fire.Fire(tag)
