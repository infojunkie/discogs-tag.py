import fire
import mutagen
import urllib.request
import json
import os
from glob import glob
from discogs_tag import __NAME__, __VERSION__

def tag(release, dir = './'):
  """Tag the audio files in dir with the given Discogs release."""
  request = urllib.request.Request(f'https://api.discogs.com/releases/{release}', headers = {
    'User-Agent': f'{__NAME__} {__VERSION__}'
  })
  with urllib.request.urlopen(request) as response:
    data = json.load(response)
    files = sorted(glob(os.path.join(dir, '*.flac')) + glob(os.path.join(dir, '*.mp3')))
    if (len(files) != len(data['tracklist'])):
      raise Exception(f'Expecting {len(data["tracklist"])} files but found {len(files)}. Aborting.')
    for n, track in enumerate(data['tracklist']):
      audio = mutagen.File(files[n], easy=True)
      audio['title'] = track['title']
      audio['artist'] = ', '.join([artist['name'] for artist in track['artists']]) if 'artists' in track else ''
      audio['tracknumber'] = track['position']
      audio.save()
    print(f'Processed {len(files)} audio files.')

def cli():
  fire.Fire(tag)
