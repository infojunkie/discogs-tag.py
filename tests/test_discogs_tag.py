from discogs_tag.cli import (
  list_files,
  read_metadata,
  apply_metadata_track,
  apply_metadata,
  parse_options,
  rename_component,
  rename_path,
  rename_file,
  get_release
)
import pytest
import json

def test_list_files():
  files = list_files('tests/glob')
  assert files == [
    'tests/glob/01.mp3',
    'tests/glob/02.flac',
    'tests/glob/04.flac',
    'tests/glob/05.mp3',
    'tests/glob/sub1/01.flac',
    'tests/glob/sub2/01.mp3'
  ]

def test_read_metadata():
  release = read_metadata([{
    'artist': ['Artist'],
    'albumartist': ['Album Artist'],
    'album': ['Album'],
    'composer': ['Composer'],
    'discnumber': ['1'],
    'genre': ['Genre'],
    'tracknumber': ['2'],
    'title': ['Title'],
    'date': ['2024']
  }], {})
  assert release['title'] == 'Album'
  assert release['artists'] == [{ 'anv': 'Album Artist' }]
  assert release['tracklist'][0]['position'] == '1-2'
  assert release['tracklist'][0]['title'] == 'Title'

  release = read_metadata([{
    'artist': ['Artist'],
    'albumartist': ['Album Artist'],
    'album': ['Album'],
    'composer': ['Composer'],
    'genre': ['Genre'],
    'tracknumber': ['0002'],
    'title': ['Title'],
    'date': ['2024']
  }], {})
  assert release['tracklist'][0]['position'] == '2'

  release = read_metadata([{
    'artist': ['Artist'],
    'albumartist': ['Album Artist'],
    'album': ['Album'],
    'composer': ['Composer'],
    'genre': ['Genre'],
    'tracknumber': ['2/10'],
    'title': ['Title'],
    'date': ['2024']
  }], {})
  assert release['tracklist'][0]['position'] == '2'

def test_apply_metadata_track():
  audio = apply_metadata_track({
    'year': 2002,
  }, {
    'title': 'Title',
    'artists': [{
      'anv': 'Artist 1'
    }, {
      'name': 'Artist 2'
    }, {
      'anv': '',
      'name': 'Artist 3 (56)'
    }],
    'position': '1-02',
    'extraartists': [{
      'role': 'Guitar',
      'name': 'Guitarist'
    }, {
      'role': 'Written-By',
      'name': 'Composer 1'
    }, {
      'role': 'Composed By',
      'name': 'Composer 2'
    }]
  }, { 'title': 'Some other title' }, 9999, parse_options({ 'skip': None }))
  assert audio['title'] == 'Title'
  assert audio['artist'] == 'Artist 1, Artist 2, Artist 3'
  assert audio['discnumber'] == '1'
  assert audio['tracknumber'] == '02'
  assert audio['composer'] == 'Composer 1, Composer 2'
  assert audio['date'] == '2002'

  audio = apply_metadata_track({
    'year': 2002,
    'artists': [{
      'anv': 'Artist 1'
    }, {
      'name': 'Artist 2'
    }, {
      'anv': '',
      'name': 'Artist 3 (56)'
    }],
  }, {
    'title': 'Title',
    'position': '1-02',
    'extraartists': [{
      'role': 'Guitar',
      'name': 'Guitarist'
    }, {
      'role': 'Written-By',
      'name': 'Composer 1'
    }, {
      'role': 'Composed By',
      'name': 'Composer 2'
    }]
  }, { 'title': 'Some other title' }, 9999, parse_options({ 'skip': None }))
  assert audio['title'] == 'Title'
  assert audio['artist'] == 'Artist 1, Artist 2, Artist 3'
  assert audio['discnumber'] == '1'
  assert audio['tracknumber'] == '02'
  assert audio['composer'] == 'Composer 1, Composer 2'
  assert audio['date'] == '2002'

  audio = apply_metadata_track({
    'year': 2002,
    'artists': [{
      'anv': 'Artist 1'
    }, {
      'name': 'Artist 2'
    }, {
      'anv': '',
      'name': 'Artist 3 (56)'
    }],
  }, {
    'title': 'Title',
    'position': '',
    'sub_tracks': [{
      'type_': 'track',
      "title": "Sub track 1",
    }, {
      'type_': 'track',
      'title': 'Sub track 2',
    }, {
      'type_': 'data',
      'title': "Not a track",
    }],
    'extraartists': [{
      'role': 'Guitar',
      'name': 'Guitarist'
    }, {
      'role': 'Written-By',
      'name': 'Composer 1'
    }, {
      'role': 'Composed By',
      'name': 'Composer 2'
    }]
  }, { 'title': 'Some other title' }, 2, parse_options({ 'skip': ['subtracks'] }))
  assert audio['title'] == 'Title: Sub track 1 / Sub track 2'
  assert audio['tracknumber'] == '2'

def test_apply_metadata():
  with open('tests/18051880.json') as release:
    data = json.load(release)

    # Test that files must match API results.
    with pytest.raises(Exception) as error:
      apply_metadata(data, [], parse_options({ 'dry': False, 'ignore': False, 'skip': None }))
    assert "Expecting 28 files" in str(error.value)

def test_count_subtracks():
  with open('tests/21343819.json') as release:
    data = json.load(release)

    # Test that files must match API results with subtracks.
    with pytest.raises(Exception) as error:
      apply_metadata(data, [], parse_options({ 'dry': False, 'ignore': False, 'skip': None }))
    assert "Expecting 18 files" in str(error.value)

  with open('tests/8582788.json') as release:
    data = json.load(release)

    # Test that files must match API results without subtracks.
    with pytest.raises(Exception) as error:
      apply_metadata(data, [], parse_options({ 'dry': False, 'ignore': False, 'skip': 'subtracks' }))
    assert "Expecting 14 files" in str(error.value)

def test_rename_component():
  assert rename_component({
    'artist': ['Artist'],
    'albumartist': ['Album Artist'],
    'album': ['Album'],
    'composer': ['Composer'],
    'discnumber': ['1'],
    'genre': ['Genre'],
    'tracknumber': [2],
    'title': ['Title'],
    'date': ['2024']
  }, '%d-%n %t', parse_options({ 'dry': True, 'ignore': False })) == '1-02 Title'

  assert rename_component({
    'artist': ['Artist'],
    'albumartist': ['Album Artist'],
    'album': ['Album'],
    'composer': ['Composer'],
    'genre': ['Genre'],
    'tracknumber': [2],
    'title': ['Title'],
    'date': ['2024']
  }, '%d-%n %t', parse_options({ 'dry': True, 'ignore': False })) == '02 Title'

  with pytest.raises(IndexError) as error:
    rename_component({
      'artist': ['Artist'],
      'albumartist': ['Album Artist'],
      'album': ['Album'],
      'composer': ['Composer'],
      'discnumber': [],
      'genre': ['Genre'],
      'tracknumber': [2],
      'title': ['Title'],
      'date': ['2024']
    }, '%d-%n %t', parse_options({ 'dry': True, 'ignore': False }))
  assert "list index out of range" in str(error.value)

def test_rename_path():
  assert rename_path('/src/path/from', {
    'artist': ['Artist'],
    'albumartist': ['Album Artist'],
    'album': ['Album'],
    'composer': ['Composer'],
    'discnumber': ['1'],
    'genre': ['Genre'],
    'tracknumber': [2],
    'title': ['Title'],
    'date': ['2024']
  }, '%z - (%y) %b/%d-%n %t', parse_options({ 'dry': True, 'ignore': False })) == ('/src/path/Album Artist - (2024) Album', '/src/path/Album Artist - (2024) Album')

  assert rename_path('/src/path/from', {
    'artist': ['Artist'],
    'albumartist': ['Album Artist'],
    'album': ['Album1 / Album2'],
    'composer': ['Composer'],
    'discnumber': ['1'],
    'genre': ['Genre'],
    'tracknumber': [2],
    'title': ['Title'],
    'date': ['2024']
  }, '%z - (%y) %b/%d-%n %t', parse_options({ 'dry': True, 'ignore': False })) == ('/src/path/Album Artist - (2024) Album1 - Album2', '/src/path/Album Artist - (2024) Album1 - Album2')

  assert rename_path('/src/path/from', {
    'artist': ['Artist'],
    'albumartist': ['Album Artist'],
    'album': ['Album1 / Album2'],
    'composer': ['Composer'],
    'discnumber': ['1'],
    'genre': ['Genre'],
    'tracknumber': [2],
    'title': ['Title']
  }, '%z - (%y) %b/%d-%n %t', parse_options({ 'dry': True, 'ignore': False })) == ('/src/path/Album Artist - Album1 - Album2', '/src/path/Album Artist - Album1 - Album2')

  assert rename_path('/src/path/from', {
    'artist': ['Artist'],
    'albumartist': ['Album Artist'],
    'album': ['Album'],
    'composer': ['Composer'],
    'discnumber': ['1'],
    'genre': ['Genre'],
    'tracknumber': [2],
    'title': ['Title'],
    'date': ['2024']
  }, '%d-%n %t', parse_options({ 'dry': True, 'ignore': False })) == ('/src/path/from', '/src/path/from')

  assert rename_path('/src/path/from', {
    'artist': ['Artist'],
    'albumartist': ['Album Artist'],
    'album': ['Album'],
    'composer': ['Composer'],
    'discnumber': ['1'],
    'genre': ['Genre'],
    'tracknumber': [2],
    'title': ['Title'],
    'date': ['2024']
  }, '%z/(%y) %b/%d-%n %t', parse_options({ 'dry': True, 'ignore': False })) == ('/src/path/Album Artist/(2024) Album', '/src/path/Album Artist')

def test_rename_file():
  assert rename_file('/src/path/from/test.flac', '/dest/path/to', {
    'artist': ['Artist'],
    'albumartist': ['Album Artist'],
    'album': ['Album'],
    'composer': ['Composer'],
    'discnumber': ['1'],
    'genre': ['Genre'],
    'tracknumber': [2],
    'title': ['Title'],
    'date': ['2024']
  }, '%z - (%y) %b/%d-%n %t', parse_options({ 'dry': True, 'ignore': False })) == '/dest/path/to/1-02 Title.flac'

  assert rename_file('/src/path/from/test.flac', '/dest/path/to', {
    'artist': ['Artist1 / Artist2'],
    'albumartist': ['Album Artist'],
    'album': ['Album'],
    'composer': ['Composer'],
    'discnumber': ['1'],
    'genre': ['Genre'],
    'tracknumber': [2],
    'title': ['Title1 / Title2'],
    'date': ['2024']
  }, '%z - (%y) %b/%d-%n %a - %t', parse_options({ 'dry': True, 'ignore': False })) == '/dest/path/to/1-02 Artist1 - Artist2 - Title1 - Title2.flac'

  assert rename_file('/src/path/from/test.flac', '/dest/path/to', {
    'artist': ['Artist'],
    'albumartist': ['Album Artist'],
    'album': ['Album'],
    'composer': ['Composer'],
    'discnumber': ['1'],
    'genre': ['Genre'],
    'tracknumber': [2],
    'title': ['Title'],
    'date': ['2024']
  }, '%z - (%y) %b/', parse_options({ 'dry': True, 'ignore': False })) == '/dest/path/to/test.flac'

def test_get_release():
  assert json.load(get_release('file:tests/16215626.json'))['id'] == 16215626
  assert json.load(get_release('16215626'))['id'] == 16215626
  assert json.load(get_release('https://api.discogs.com/releases/16215626'))['id'] == 16215626
  assert json.load(get_release('https://www.discogs.com/release/16215626-Pink-Floyd-Wish-You-Were-Here'))['id'] == 16215626
