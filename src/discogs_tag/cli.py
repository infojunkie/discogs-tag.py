import fire
import mutagen
import urllib.request
import json
import os
from glob import glob

def tag(release, dir = ''):
  request = urllib.request.Request(f'https://api.discogs.com/releases/{release}', headers = {
    'User-Agent': 'discogs-tag'
  })
  with urllib.request.urlopen(request) as response:
    data = json.load(response)
    files = sorted(glob(os.path.join(dir, '*.flac')) + glob(os.path.join(dir, '*.mp3')))
    if (len(files) != len(data['tracklist'])):
      raise Exception(f'Expecting {len(data["tracklist"])} files but found {len(files)}. Aborting.')
    for n, track in enumerate(data['tracklist']):
      audio = mutagen.File(files[n], easy=True)
      audio['title'] = track['title']
      audio['artist'] = ', '.join([artist['name'] for artist in track['artists']])
      audio['tracknumber'] = track['position']
      audio.save()

def cli():
  fire.Fire(tag)
