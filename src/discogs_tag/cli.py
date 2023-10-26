import fire
import mutagen
import urllib.request
import json
import os
from pprint import pprint
import glob
from discogs_tag import __NAME__, __VERSION__

def tag(release, dir = './', dry = False):
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
    tracks = list(filter(lambda t: t['type_'] == 'track', data['tracklist']))
    if (len(files) != len(tracks)):
      raise Exception(f'Expecting {len(tracks)} files but found {len(files)}. Aborting.')
    for n, track in enumerate(tracks):
      audio = mutagen.File(files[n], easy=True)
      audio['title'] = track['title']
      if 'artists' in track:
        audio['artist'] = ', '.join([artist_name(artist) for artist in track['artists']])
      positions = track['position'].split('-')
      audio['tracknumber'] = positions[-1]
      if (len(positions) > 1):
        audio['discnumber'] = positions[0]
      composers = ', '.join([artist_name(composer) for composer in filter(lambda a: a['role'].casefold() == 'Written-By'.casefold(), track['extraartists'])]) if 'extraartists' in track else None
      if (composers):
        audio['composer'] = composers
      if (dry):
        pprint(audio)
      else:
        audio.save()

    if (not dry):
      print(f'Processed {len(files)} audio files.')

def artist_name(artist):
  return artist['anv'] or artist['name']

def cli():
  fire.Fire(tag)
